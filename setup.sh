#!/bin/bash

usage() { echo "Usage: $0 -h <IP/domain string> [-p DB password]" 1>&2; exit 1; }

if ! [ -x "$(command -v docker)" ]; then
    echo "Please install docker before continuing"
    exit 1
fi

if ! [ -x "$(command -v docker-compose)" ]; then
    echo "Please install docker-compose before continuing"
    exit 1
fi

while getopts ":h:p:" o; do
    case "${o}" in
        h)
            h=${OPTARG}
            ;;
        p)
            p=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

if [ -z "${h}" ]; then
    usage
fi

s=$(python -c "import random;secret=''.join('%02x' % random.randrange(256) for i in xrange(32));print secret")

echo "Setting up with the following parameters:"
echo "IP/Domain: ${h}"
if ! [ -z "${p}" ]; then
    echo "DB Password: ${p}"
fi
echo "App Secret: ${s}"

sed -i '' "s/SECRET HERE/$s/g" main.py

if ! [ -z "${p}" ]; then
    sed -i '' "s/dbpassword/$p/g" docker-compose.yml
    sed -i '' "s/dbpassword/$p/g" model.py
fi

sed -i '' "s/ssrftest.com/$h/g" handlers/target.py
sed -i '' "s/ssrftest.com/$h/g" templates/target/index.html

./build-docker.sh

docker-compose up
