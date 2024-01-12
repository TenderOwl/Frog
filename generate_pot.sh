function generate_po()
{
    cd po
    git pull https://hosted.weblate.org/git/frog/frog/default
    >frog.pot
    for file in ../data/org.github.tenderowl.frog.gschema.xml ../data/*.in ../data/ui/*.blp ../frog/*.py ../frog/services/*.py ../frog/types/*.py ../frog/widgets/*.py
    do
        xgettext --add-comments --keyword=_ --keyword=C_:1c,2 --from-code=UTF-8 -j $file -o frog.pot
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
