#!/bin/bash
echo "Hello, this installs ffmpeg to the system default path (/usr/local/bin)."
arch=$(uname -m | tr "[:upper:]" "[:lower:]")
os=$(uname | tr "[:upper:]" "[:lower:]")
client=$(command -v curl || command -v wget)
url=https://api.github.com/repos/iwconfig/dlffmpeg/releases/latest
tmp=/tmp/QUICK_DLFFMPEG
if [[ "$arch" == *arm* ]]; then
		[[ ${arch//[^0-9]/} -lt 7 ]] && echo "Sorry, only ARM version >= armv7l is supported (armhf). You are using $arch." && exit 1
		arch='armhf'; fi
[[ -f $tmp ]] && rm $tmp
if [[ -x $client ]]; then
		[[ "$client" == *wget ]] && client+=" -q -O -" || client+=" -# -L"
		IFS=' ' read -r -a github_urls <<< "$($client -s "$url" | grep 'browser_' | cut -d\" -f4 | tr '\n' ' ')"
		[[ "$os" == "darwin" ]] && for url in "${github_urls[@]}"; do [[ "$url" == *macosx* ]] && url=$url && break; done
		if [[ "$os" == "linux" ]]; then
				if [[ "$arch" == "armhf" ]]; then
						for url in "${github_urls[@]}"; do [[ "$url" == *armhf* ]] && url=$url && break; done
				else
						for url in "${github_urls[@]}"; do [[ "$url" == *linux* ]] && url=$url && break; done; fi; fi
		echo Downloading "$url"
		$client "$url" >$tmp && chmod +x $tmp && sudo $tmp && rm $tmp
else
		echo Please install curl or wget. && exit 1; fi