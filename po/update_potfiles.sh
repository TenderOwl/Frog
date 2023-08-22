#!/bin/bash

DOMAIN_EXTENSION="com.github"
AUTHOR="tenderowl"
APPNAME="frog"
APPID="${DOMAIN_EXTENSION}.${AUTHOR}.${APPNAME}"

if [ "$1" == "-h" ]; then
    echo "Usage: $0 [lang]"
    exit
fi
lang="$1"

rm *.pot

version=$(grep -Fm 1 "version: " ../meson.build | grep -v "meson" | grep -o "'.*'" | sed "s/'//g")

find ../$APPNAME -iname "*.py" | xargs xgettext --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-python.pot
# find ../data/ui -iname "*.glade" -or -iname "*.xml" -or -iname "*.ui" | xargs xgettext --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-glade.pot -L Glade
find ../data/ui -iname "*.blp" | xargs xgettext --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-blueprint.pot -L Python
# find ../data/ui -iname "*.ui.in" | xargs xgettext --no-wrap --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-ui-xml.pot
find ../data/ -iname "*.desktop.in" | xargs xgettext --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-desktop.pot -L Desktop
find ../data/ -iname "*.appdata.xml.in" | xargs xgettext --no-wrap --package-name=$APPNAME --package-version=$version --from-code=UTF-8 --output=$APPNAME-appdata.pot

msgcat --use-first $APPNAME-python.pot $APPNAME-blueprint.pot $APPNAME-desktop.pot $APPNAME-appdata.pot > $APPID.pot

sed 's/#: //g;s/:[0-9]*//g;s/\.\.\///g' <(grep -F "#: " $APPID.pot) | sort | uniq | sed 's/ /\n/g' | uniq > POTFILES.in
cat POTFILES.in | sort | uniq > POTFILES
rm POTFILES.in

#if [ ! -z "${lang}" ]; then
#    [ -f "${lang}.po" ] && mv "${lang}.po" "${lang}.po.old"
#    msginit --locale=$lang --input $APPID.pot
#    if [ -f "${lang}.po.old" ]; then
#        mv "${lang}.po" "${lang}.po.new"
#        msgmerge -N "${lang}.po.old" "${lang}.po.new" > ${lang}.po
#        rm "${lang}.po.old" "${lang}.po.new"
#    fi
#    sed -i 's/ASCII/UTF-8/' "${lang}.po"
#fi
mv $APPID.pot $APPNAME.pot.bak
rm *.pot
mv $APPNAME.pot.bak $APPNAME.pot
