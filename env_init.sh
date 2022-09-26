export OUTSCALE_ACCESSKEYID=$(security find-generic-password -w -s osc -a 'ak')
export OUTSCALE_SECRETKEYID=$(security find-generic-password -w -s osc -a 'sk')
export OUTSCALE_REGION="eu-west-2"