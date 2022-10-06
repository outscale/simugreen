"""

This file is used to parse the mpeg-ts file in order to get the
delta between PCR and PTS and in order to get stream element statistics

MPEG-TS stream is the usual format used for IPTV (TV over IP), the format
is basic, here some elements:
    - MPEG-TS is composed of 188 Bytes packets;
    - Each packet describes an stream elements (Video, Audio, Subtitles,
    Program information, ...);
    - All packets are not used for streaming a video...
    - Each video or audio packet own a PTS (timestamp) in order to know
    when the element stream is played;
    - Usually video and audio packets are played following a given clock
    called PCR;
    - During streaming (real time), the delta between the packet arrival
    and the PCR is very important, this is something usually monitored
    in the stream pipeline.

"""

import sys
import struct
import logging 
from optparse import OptionParser

class SystemClock:
    def __init__(self):
        self.PCR = 0x0
    def setPCR(self, PCR):
        self.PCR = PCR
    def getPCR(self):
        return self.PCR

class PESPacketInfo:
    def __init__(self):
        self.PTS = 0
        self.streamID = 0
        self.AUType = ""
    def setPTS(self, PTS):
        self.PTS = PTS
    def getPTS(self):
        return self.PTS
    def setStreamID(self, streamID):
        self.streamID = streamID
    def setAUType(self, auType):
        self.AUType = auType
    def getStreamID(self):
        return self.streamID
    def getAUType(self):
        return self.AUType

def readFile(fileHandle, startPos, width):
    fileHandle.seek(startPos,0)
    if width == 4:
        string = fileHandle.read(4)
        if len(string) != 4:
            raise IOError
        return struct.unpack('>L',string[:4])[0]
    elif width == 2:
        string = fileHandle.read(2)
        if len(string) != 2:
            raise IOError
        return struct.unpack('>H',string[:2])[0]
    elif width == 1:
        string = fileHandle.read(1)
        if len(string) != 1:
            raise IOError
        return struct.unpack('>B',string[:1])[0]

def parseAdaptation_Field(fileHandle, startPos, PCR):
    n = startPos
    flags = 0
    adaptation_field_length = readFile(fileHandle,n,1)
    if adaptation_field_length > 0:
        flags = readFile(fileHandle,n+1,1)
        PCR_flag = (flags>>4)&0x1
        if PCR_flag == 1:
            time1 = readFile(fileHandle,n+2,1)
            time2 = readFile(fileHandle,n+3,1)
            time3 = readFile(fileHandle,n+4,1)
            time4 = readFile(fileHandle,n+5,1)
            time5 = readFile(fileHandle,n+6,1)
            time6 = readFile(fileHandle,n+7,1)
           
            PCR_val  = time1 << 25
            PCR_val |= time2 << 17
            PCR_val |= time3 << 9
            PCR_val |= time4 << 1
            PCR_val |= (time5 & 0x80) >> 7

            PCR_val *= 300
            PCR_val |= (time5 & 0x01) << 8
            PCR_val |= time6

            PCR.setPCR(PCR_val)
    return [adaptation_field_length + 1, flags]

def getPTS(fileHandle, startPos):
    n = startPos

    time1 = readFile(fileHandle,n,1)
    time2 = readFile(fileHandle,n+1,1)
    time3 = readFile(fileHandle,n+2,1)
    time4 = readFile(fileHandle,n+3,1)
    time5 = readFile(fileHandle,n+4,1)

    PTS   = (time1 & 0x0E) >> 1 
    PTS <<= 8
    PTS  |= time2
    PTS <<= 7
    PTS  |= (time3 & 0xFE) >> 1
    PTS <<= 8
    PTS  |= time4
    PTS <<= 7
    PTS  |= (time5 & 0xFE) >> 1

    return PTS

def parseIndividualPESPayload(fileHandle, startPos):
    n = startPos
    local = readFile(fileHandle,n,4)
    k = 0
    while((local&0xFFFFFF00) != 0x00000100):
        k += 1;
        if (k > 100):
            return "Unknown AU type"
        local = readFile(fileHandle,n+k,4)

    if(((local&0xFFFFFF00) == 0x00000100)&(local&0x1F == 0x9)):
        primary_pic_type = readFile(fileHandle,n+k+4,1)
        primary_pic_type = (primary_pic_type&0xE0)>>5
        if (primary_pic_type == 0x0):
            return "IDR_picture"
        else:
            return "non_IDR_picture"

def parsePESHeader(fileHandle, startPos,PESPktInfo):
    n = startPos
    stream_ID = readFile(fileHandle, n+3, 1)
    PES_packetLength = readFile(fileHandle, n+4, 2)
    PESPktInfo.setStreamID(stream_ID)

    k = 6

    if ((stream_ID != 0xBC)& \
        (stream_ID != 0xBE)& \
        (stream_ID != 0xF0)& \
        (stream_ID != 0xF1)& \
        (stream_ID != 0xFF)& \
        (stream_ID != 0xF9)& \
        (stream_ID != 0xF8)):

        PES_packet_flags = readFile(fileHandle, n+5, 4)
        PTS_DTS_flag = ((PES_packet_flags>>14)&0x3)
        PES_header_data_length = PES_packet_flags&0xFF

        k += PES_header_data_length + 3

        if (PTS_DTS_flag == 0x2):
            PTS = getPTS(fileHandle, n+9)
            PESPktInfo.setPTS(PTS)

        elif (PTS_DTS_flag == 0x3):
            PTS = getPTS(fileHandle, n+9)
            PESPktInfo.setPTS(PTS)

            DTS = getPTS(fileHandle, n+14)
        else:
            k = k
            return

        auType = parseIndividualPESPayload(fileHandle, n+k)
        PESPktInfo.setAUType(auType)

def parsePATSection(fileHandle, k):

    local = readFile(fileHandle,k,4)
    table_id = (local>>24)
    if (table_id != 0x0):
        logging.error ('Ooops! error in parsePATSection()!')
        return

    logging.debug ('------- PAT Information -------')
    section_length = (local>>8)&0xFFF
    logging.debug ('section_length = %d' %section_length)

    transport_stream_id = (local&0xFF) << 8;
    local = readFile(fileHandle, k+4, 4)
    transport_stream_id += (local>>24)&0xFF
    transport_stream_id = (local >> 16)
    version_number = (local>>17)&0x1F
    current_next_indicator = (local>>16)&0x1
    section_number = (local>>8)&0xFF
    last_section_number = local&0xFF;
    logging.debug ('section_number = %d, last_section_number = %d' %(section_number, last_section_number))

    length = section_length - 4 - 5
    j = k + 8

    while (length > 0):
        local = readFile(fileHandle, j, 4)
        program_number = (local >> 16)
        program_map_PID = local & 0x1FFF
        logging.debug ('program_number = 0x%X' %program_number)
        if (program_number == 0):
            logging.debug ('network_PID = 0x%X' %program_map_PID)
        else:
            logging.debug ('program_map_PID = 0x%X' %program_map_PID)
        length = length - 4;
        j += 4
        
        logging.debug ('')

def parsePMTSection(fileHandle, k):

    local = readFile(fileHandle,k,4)

    table_id = (local>>24)
    if (table_id != 0x2):
        logging.error ('Ooops! error in parsePATSection()!')
        return

    logging.debug ('------- PMT Information -------')

    section_length = (local>>8)&0xFFF
    logging.debug ('section_length = %d' %section_length)

    program_number = (local&0xFF) << 8;

    local = readFile(fileHandle, k+4, 4)

    program_number += (local>>24)&0xFF
    logging.debug ('program_number = %d' %program_number)

    version_number = (local>>17)&0x1F
    current_next_indicator = (local>>16)&0x1
    section_number = (local>>8)&0xFF
    last_section_number = local&0xFF;
    logging.debug ('section_number = %d, last_section_number = %d' %(section_number, last_section_number))

    local = readFile(fileHandle, k+8, 4)

    PCR_PID = (local>>16)&0x1FFF
    logging.debug ('PCR_PID = 0x%X' %PCR_PID)
    program_info_length = (local&0xFFF)
    logging.debug ('program_info_length = %d' %program_info_length)

    n = program_info_length
    m = k + 12;
    while (n>0):
        descriptor_tag = readFile(fileHandle, m, 1)
        descriptor_length = readFile(fileHandle, m+1, 1)
        logging.debug ('descriptor_tag = %d, descriptor_length = %d' %(descriptor_tag, descriptor_length))
        n -= descriptor_length + 2
        m += descriptor_length + 2

    j = k + 12 + program_info_length
    length = section_length - 4 - 9 - program_info_length

    while (length > 0):
        local1 = readFile(fileHandle, j, 1)
        local2 = readFile(fileHandle, j+1, 4)

        stream_type = local1;
        elementary_PID = (local2>>16)&0x1FFF
        ES_info_length = local2&0xFFF

        logging.debug ('stream_type = 0x%X, elementary_PID = 0x%X, ES_info_length = %d' %(stream_type, elementary_PID, ES_info_length))
        n = ES_info_length
        m = j+5;
        while (n>0):
            descriptor_tag = readFile(fileHandle, m, 1)
            descriptor_length = readFile(fileHandle, m+1, 1)
            logging.debug ('descriptor_tag = %d, descriptor_length = %d' %(descriptor_tag, descriptor_length))
            n -= descriptor_length + 2
            m += descriptor_length + 2

        j += 5 + ES_info_length
        length -= 5 + ES_info_length

    logging.debug ('')

def parseSITSection(fileHandle, k):
    local = readFile(fileHandle,k,4)

    table_id = (local>>24)
    if (table_id != 0x7F):
        logging.error ('Ooops! error in parseSITSection()!')
        return

    logging.debug ('------- SIT Information -------')

    section_length = (local>>8)&0xFFF
    logging.debug ('section_length = %d' %section_length)
    local = readFile(fileHandle, k+4, 4)

    section_number = (local>>8)&0xFF
    last_section_number = local&0xFF;
    logging.debug ('section_number = %d, last_section_number = %d' %(section_number, last_section_number))
    local = readFile(fileHandle, k+8, 2)
    transmission_info_loop_length = local&0xFFF
    logging.debug ('transmission_info_loop_length = %d' %transmission_info_loop_length)

    n = transmission_info_loop_length
    m = k + 10;
    while (n>0):
        descriptor_tag = readFile(fileHandle, m, 1)
        descriptor_length = readFile(fileHandle, m+1, 1)
        logging.debug ('descriptor_tag = %d, descriptor_length = %d' %(descriptor_tag, descriptor_length))
        n -= descriptor_length + 2
        m += descriptor_length + 2

    j = k + 10 + transmission_info_loop_length
    length = section_length - 4 - 7 - transmission_info_loop_length

    while (length > 0):
        local1 = readFile(fileHandle, j, 4)
        service_id = (local1>>16)&0xFFFF;
        service_loop_length = local1&0xFFF
        logging.debug ('service_id = %d, service_loop_length = %d' %(service_id, service_loop_length))

        n = service_loop_length
        m = j+4;
        while (n>0):
            descriptor_tag = readFile(fileHandle, m, 1)
            descriptor_length = readFile(fileHandle, m+1, 1)
            logging.debug ('descriptor_tag = %d, descriptor_length = %d' %(descriptor_tag, descriptor_length))
            n -= descriptor_length + 2
            m += descriptor_length + 2

        j += 4 + service_loop_length
        length -= 4 + service_loop_length
    logging.debug ('')

def getDeltaPcrPts(pid, pcr, pts):
    listDelta = []
    pcrIdx = 0

    for packet in pts:
        if (packet['pid'] != pid):
            continue
        while ((pcr[pcrIdx]['packet'] < packet['packet']) & (pcrIdx < len(pcr) - 1)):
            pcrIdx += 1
        if (pcr[pcrIdx]['packet'] < packet['packet']):
            break
        listDelta.append (packet['pts'] / 90 - pcr[pcrIdx]['pcr'] / 27000)
    return listDelta

def getDeltaStats (listDelta):
    total = 0
    minVal = 100000
    maxVal = 0
    
    for delta in listDelta:
        total += delta
        if (delta < minVal):
            minVal = delta
        if (delta > maxVal):
            maxVal = delta
    return { 'min': int(minVal), 'max': int(maxVal), 'average':int(total/len(listDelta))}

def getTrackStat (pid, count, pts):
    firstPacket = 0
    lastPacket = len(pts)-1

    while (pts[firstPacket]['pid'] != pid):
        firstPacket += 1

    while (pts[lastPacket]['pid'] != pid):
        lastPacket -= 1

    duration = pts[lastPacket]['pts'] / 90 - pts[firstPacket]['pts'] / 90
    size = count * 188

    return { 'duration': int(duration / 1000), 'size': int(size), 'bandwidth': int((8 * 1000 * size) / duration) }

def getPidStats (pidList, pcr, pts):
    stats = []

    for pid in pidList:
        deltaPid = getDeltaPcrPts(pid['pid'], pcr, pts)
        deltaStats = getDeltaStats (deltaPid)
        stat = getTrackStat (pid['pid'], pid['count'], pts)

        stats.append ({'pid': pid['pid'], 'deltaPcrPts': deltaStats, 'duration': stat['duration'], 'size': stat['size'], 'bandwidth': stat['bandwidth'] })

    return stats

def parsePcrPts(fileHandle):

    PCR = SystemClock()
    PESPktInfo = PESPacketInfo()

    n = 0
    packet_size = 188

    packetCount = 0

    PESPidList = []
    PTSList = []
    PCRList = []

    try:
        while(True):

            PacketHeader = readFile(fileHandle,n,4)

            syncByte = (PacketHeader>>24)
            if (syncByte != 0x47):
                logging.error ('Ooops! Can NOT found Sync_Byte! maybe something wrong with the file')
                break

            payload_unit_start_indicator = (PacketHeader>>22)&0x1

            PID = ((PacketHeader>>8)&0x1FFF)

            adaptation_fieldc_trl = ((PacketHeader>>4)&0x3)
            Adaptation_Field_Length = 0

            if (adaptation_fieldc_trl == 0x2)|(adaptation_fieldc_trl == 0x3):
                [Adaptation_Field_Length, flags] = parseAdaptation_Field(fileHandle,n+4,PCR)
            
                if (((flags>>4)&0x1)):
                    discontinuity = False
                    if (((flags>>7)&0x1)):
                        discontinuity = True

                    logging.debug ('PCR packet, packet No. %d, PID = 0x%x, PCR = 0x%X discontinuity = %s' \
                            %(packetCount, PID, PCR.PCR, discontinuity))
                    PCRList.append ({'packet':packetCount,'pid':PID, 'pcr':PCR.PCR, 'discontinuity':discontinuity})

            if (adaptation_fieldc_trl == 0x1)|(adaptation_fieldc_trl == 0x3):

                PESstartCode = readFile(fileHandle,n+Adaptation_Field_Length+4,4)

                if ((PESstartCode&0xFFFFFF00) == 0x00000100):

                    if (payload_unit_start_indicator == 1):
                        parsePESHeader(fileHandle, n+Adaptation_Field_Length+4, PESPktInfo)
                        logging.debug ('PES start, packet No. %d, PID = 0x%x, PTS = 0x%X' \
                        %(packetCount, PID, PESPktInfo.PTS))
                        PTSList.append ({'packet':packetCount,'pid':PID, 'pts':PESPktInfo.PTS})

                    pidFound = False
                    for index in PESPidList:
                        if (index['pid'] == PID):
                            pidFound = True
                            break

                    if not pidFound: 
                        PESPidList.append ({'pid':PID, 'count':0})

                elif (((PESstartCode&0xFFFFFF00) != 0x00000100)& \
                    (payload_unit_start_indicator == 1)):

                    pointer_field = (PESstartCode >> 24)
                    table_id = readFile(fileHandle,n+Adaptation_Field_Length+4+1+pointer_field,1)

                    if ((table_id == 0x0)&(PID != 0x0)):
                        logging.warning ('Ooops!, Something wrong in packet No. %d' %packetCount)

                    k = n+Adaptation_Field_Length+4+1+pointer_field

                    if (table_id == 0x0):
                        logging.debug ('pasing PAT Packet! packet No. %d, PID = 0x%X' %(packetCount, PID))
                        parsePATSection(fileHandle, k)

                    elif (table_id == 0x2):
                        logging.debug ('pasing PMT Packet! packet No. %d, PID = 0x%X' %(packetCount, PID))
                        parsePMTSection(fileHandle, k)
                    
                    elif (table_id == 0x7F):
                        logging.debug ('pasing SIT Packet! packet No. %d, PID = 0x%X' %(packetCount, PID))
                        parseSITSection(fileHandle, k)

            n += packet_size
            for index in PESPidList:
                if (index['pid'] == PID):
                    index['count'] += 1
                    break

            packetCount += 1
   
    except IOError:
        logging.info ('IO error! maybe reached EOF')
        return [PESPidList, PCRList, PTSList]
    else:
        fileHandle.close()
    return [PESPidList, PCRList, PTSList]

def parse_transport_stream(filename):

    fileHandle = open(filename,'rb')
    
    [pesPidList, pcr, pts] = parsePcrPts(fileHandle)
    stats = getPidStats(pesPidList, pcr, pts)
    logging.info (stats)
    return stats


