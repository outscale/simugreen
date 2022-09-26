docker run -d -it --init -p 3000:3000 -v "/data/vscode:/home/workspace:cached" -v "/data/code:/code:cached" vscode
