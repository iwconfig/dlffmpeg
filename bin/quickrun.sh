#!/bin/bash
arch=$(uname -m)
os=$(uname)
client=$(command -v curl || command -v wget)
url=https://api.github.com/repos/iwconfig/dlffmpeg/releases/latest
tmp=/tmp/QUICK_DLFFMPEG
if [[ "$arch" == *arm* ]]; then
    [[ ${arch//[^0-9]/} < 7 ]] && echo "Sorry, only ARM version >= armv7l is supported (armhf). You are using $arch." && exit 1
    arch='armhf'
fi
[[ -x $tmp ]] && $tmp && rm $tmp && exit 0 || [[ ! -x $tmp ]] && : || exit 1
if [[ -x $client ]]; then
    if [[ "$client" == *wget ]]; then
        client+=" -q -O -"
    else
        client+=" -# -L"
    fi
    IFS=' ' read -r -a github_urls <<< $($client -s "$url" | grep 'browser_' | cut -d\" -f4)
    for url in "${github_urls[@]}"; do
        if [[ ! "$arch" == "armhf" ]]; then
            [[ "$url" == *linux* ]] && [[ "$url" != *armhf* ]] && url=$url || \
            [[ "$url" == *macosx* ]] && url=$url && break
        else
            [[ "$url" == *armhf* ]] && url=$url && break
        fi
    done
    echo Downloading $url
    $client "$url" >$tmp && chmod +x $tmp
    $tmp && rm $tmp
else
    echo Please install curl or wget.
    exit 1
fi