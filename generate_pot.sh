function generate_po()
{
    cd po
    git pull https://hosted.weblate.org/git/frog/frog/default
    >frog.pot
    for file in ../data/org.github.tenderowl.frog.gschema.xml ../data/*.in ../data/*.ui ../frog/*.py
    do
        xgettext --from-code=UTF-8 -j $file -o frog.pot
    done
    >LINGUAS
    for po in *.po
    do
        msgmerge -N $po frog.pot > /tmp/$$language_new.po
        mv /tmp/$$language_new.po $po
        language=${po%.po}
        echo $language >>LINGUAS
    done
}

generate_po
