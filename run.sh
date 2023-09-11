# Image Settings
imageName=crowdin-top-contributor-listing
containerName=Crowdin-Top-Contributor-Listing
imageVersion=1.0

docker build --no-cache -f Dockerfile -t $imageName:$imageVersion --target runtime .
docker run -d --restart=always \
    -e TZ=Asia/Shanghai \
    --name="$containerName-$imageVersion" \
    $imageName:$imageVersion