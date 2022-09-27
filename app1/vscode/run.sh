docker run -d -it --init -p 3000:3000 -v "/data/vscode:/home/workspace:cached" -v "/home/outscale:/outscale:cached" vscode
