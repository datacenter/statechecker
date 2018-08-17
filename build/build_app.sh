#!/bin/bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/../"
# change working directory to root of project
cd $BASE_DIR
source $BASE_DIR/build/build_common.sh
TMP_DIR="/tmp/appbuild/"

self=$0
docker_image=""
intro_video=""
private_key=""
enable_proxy="0"
relax_build_checks="0"
build_standalone="0"
standalone_http_port="5000"
standalone_https_port="5001"

# build and deploy standalone container
function build_standalone_container() {
    set -e
    log "deploying standalone container $APP_VENDOR_DOMAIN/$APP_ID:$APP_VERSION"

    # cp app.json to Service directory for consumption by config.py
    cp ./app.json ./Service/

    # build docker container
    log "building container"
    docker_name=`echo "aci/$APP_ID:$APP_VERSION" | tr '[:upper:]' '[:lower:]'`
    container_name=`echo "$APP_ID\_$APP_VERSION" | tr '[:upper:]' '[:lower:]'`
    ba="--build-arg APP_MODE=0 "
    if [ "$enable_proxy" == "1" ] ; then
        if [ "$https_proxy" ] ; then ba="$ba --build-arg https_proxy=$https_proxy" ; fi
        if [ "$http_proxy" ] ; then ba="$ba --build-arg http_proxy=$http_proxy" ; fi
        if [ "$no_proxy" ] ; then ba="$ba --build-arg no_proxy=$no_proxy" ; fi
    fi
    log "cmd: docker build -t $docker_name $ba ./build/"
    docker build -t $docker_name $ba ./build/

    # run the container with volume mount based on BASE_DIR and user provided http and https ports
    local cmd="docker run -dit --restart always --name $container_name "
    cmd="$cmd -v $BASE_DIR/Service:/home/app/src/Service:ro "
    cmd="$cmd -v $BASE_DIR/UIAssets:/home/app/src/UIAssets.src:ro "
    cmd="$cmd -v $BASE_DIR/build:/home/app/src/build:ro "
    cmd="$cmd -p $standalone_http_port:80 "
    cmd="$cmd -p $standalone_https_port:443 "
    cmd="$cmd $docker_name "
    log "starting container: $cmd"
    eval $cmd
}

# build aci app
function build_app() {
    set -e
    log "building application $APP_VENDOR_DOMAIN/$APP_ID"
    
    # create workspace directory, setup required app-mode directories, and copy over required files
    log "building workspace/copying files to $TMP_DIR/$APP_ID"
    rm -rf $TMP_DIR/$APP_ID
    rm -rf $TMP_DIR/$APP_ID.build
    mkdir -p $TMP_DIR/$APP_ID/UIAssets
    mkdir -p $TMP_DIR/$APP_ID/Service
    mkdir -p $TMP_DIR/$APP_ID/Image
    mkdir -p $TMP_DIR/$APP_ID/Legal
    mkdir -p $TMP_DIR/$APP_ID/Media/Snapshots
    mkdir -p $TMP_DIR/$APP_ID/Media/Readme
    mkdir -p $TMP_DIR/$APP_ID/Media/License
    mkdir -p $TMP_DIR/$APP_ID.build
    
    # copy source code to service
    cp -rp ./Service/* $TMP_DIR/$APP_ID/Service/
    cp -p ./app.json $TMP_DIR/$APP_ID/
    # include app.json in Service directory for config.py to pick up required variables
    cp -p ./app.json $TMP_DIR/$APP_ID/Service/

    # create media and legal files
    # (note, snapshots are required in order for intro_video to be displayed on appcenter
    if [ "$(ls -A ./Legal)" ] ; then 
        cp -p ./Legal/* $TMP_DIR/$APP_ID/Legal/
    fi
    if [ "$(ls -A ./Media/Snapshots)" ] ; then 
        cp -p ./Media/Snapshots/* $TMP_DIR/$APP_ID/Media/Snapshots/
    fi
    if [ "$(ls -A ./Media/Readme)" ] ; then 
        cp -p ./Media/Readme/* $TMP_DIR/$APP_ID/Media/Readme/
    fi
    if [ "$(ls -A ./Media/License)" ] ; then 
        cp -p ./Media/License/* $TMP_DIR/$APP_ID/Media/License/
    fi

    if [ "$intro_video" ] ; then
        log "adding intro video $intro_video"
        mkdir -p $TMP_DIR/$APP_ID/Media/IntroVideo
        cp $intro_video $TMP_DIR/$APP_ID/Media/IntroVideo/IntroVideo.mp4
        chmod 777 $TMP_DIR/$APP_ID/Media/IntroVideo/IntroVideo.mp4
    elif [ -f ./Media/IntroVideo/IntroVideo.mp4 ] ; then 
        log "adding default intro video"
        mkdir -p $TMP_DIR/$APP_ID/Media/IntroVideo
        cp ./Media/IntroVideo/IntroVideo.mp4 $TMP_DIR/$APP_ID/Media/IntroVideo/IntroVideo.mp4
        chmod 777 $TMP_DIR/$APP_ID/Media/IntroVideo/IntroVideo.mp4
    fi

    # this project performs frontend angular build from source in UIAssets
    if [ "$(ls -A ./UIAssets)" ] ; then
        mkdir -p $TMP_DIR/$APP_ID.build/UIAssets
        local bf_tmp="$TMP_DIR/$APP_ID.build/UIAssets/"
        local bf_src="$BASE_DIR/UIAssets/"
        local bf_dst="$TMP_DIR/$APP_ID/UIAssets/"
        ./build/build_frontend.sh -s $bf_src -d $bf_dst -t $bf_tmp -m "app"
        # need to manually copy over logo.png into UIAssets folder
        if [ -f "$BASE_DIR/UIAssets/logo.png" ] ; then
            cp -p $BASE_DIR/UIAssets/logo.png $bf_dst
        fi
    fi

    # build docker container
    if [ "$docker_image" ] ; then
        log "saving docker container image to application"
        cp $docker_image > $TMP_DIR/$APP_ID/Image/aci_appcenter_docker_image.tgz
    else
        log "building container"
        docker_name=`echo "aci/$APP_ID:$APP_VERSION" | tr '[:upper:]' '[:lower:]'`
        if [ "$enable_proxy" == "1" ] ; then
            ba=""
            if [ "$https_proxy" ] ; then ba="$ba --build-arg https_proxy=$https_proxy" ; fi
            if [ "$http_proxy" ] ; then ba="$ba --build-arg http_proxy=$http_proxy" ; fi
            if [ "$no_proxy" ] ; then ba="$ba --build-arg no_proxy=$no_proxy" ; fi
            log "cmd: docker build -t $docker_name $ba --build-arg APP_MODE=1 ./"
            docker build -t $docker_name $ba --build-arg APP_MODE=1 ./build/
        else
            log "cmd: docker build -t $docker_name --build-arg APP_MODE=1 ./"
            docker build -t $docker_name --build-arg APP_MODE=1 ./build/
        fi
        log "saving docker container image to application"
        docker save $docker_name | gzip -c > $TMP_DIR/$APP_ID/Image/aci_appcenter_docker_image.tgz
    fi

    # execute packager
    log "packaging application"
    tar -zxf ./build/app_package/cisco_aci_app_tools-1.1_min.tar.gz -C $TMP_DIR/$APP_ID.build/ 
    if [ "$private_key" ] ; then
        python $TMP_DIR/$APP_ID.build/cisco_aci_app_tools-1.1_min/tools/aci_app_packager.py -f $TMP_DIR/$APP_ID -p $private_key
    else
        python $TMP_DIR/$APP_ID.build/cisco_aci_app_tools-1.1_min/tools/aci_app_packager.py -f $TMP_DIR/$APP_ID
    fi

    # cleanup
    rm -rf $TMP_DIR/$APP_ID.build
    rm -rf $TMP_DIR/$APP_ID
   
    log "build complete: `ls -a $TMP_DIR/*.aci`"

    set +e
}

# help options
function display_help() {
    echo ""
    echo "Help documentation for $self"
    echo "    -i [image] docker image to bundled into app (.tgz format)"
    echo "    -v [file] path to intro video (.mp4 format)"
    echo "    -p [file] private key uses for signing app"
    echo "    -x send local environment proxy settings to container during build"
    echo "    -r relax build checks (ensure tools are present but skip version check)"
    echo "    -s build and deploy container for standalone mode"
    echo ""
    exit 0
}


optspec=":i:v:p:hxrs"
while getopts "$optspec" optchar; do
  case $optchar in
    i)
        docker_image=$OPTARG
        if [ ! -f $docker_image ] ; then
            echo "" >&2
            echo "docker image '$docker_image' not found, aborting build" >&2
            echo "" >&2
            exit 1 
        fi
        ;;
    v) 
        intro_video=$OPTARG
        if [ ! -f $intro_video ] ; then
            echo "" >&2
            echo "intro video '$intro_video' not found, aborting build" >&2
            echo "" >&2
            exit 1
        fi
        ;;
    p)
        private_key=$OPTARG
        if [ ! -f $private_key ] ; then
            echo "" >&2
            echo "private key '$private_key' not found, aborting build" >&2
            echo "" >&2
            exit 1
        fi
        ;;
    x)
        enable_proxy="1"
        ;;
    r)
        relax_build_checks="1"
        ;;
    s)
        build_standalone="1"
        ;;
    h)
        display_help
        exit 0
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        exit 1
        ;;
    \?)
        echo "Invalid option: \"-$OPTARG\"" >&2
        exit 1
        ;;
  esac
done

# check depedencies first and then execute build
if [ "$build_standalone" == "1" ] ; then
    check_build_tools "backend"
    build_standalone_container
else
    check_build_tools 
    build_app
fi

