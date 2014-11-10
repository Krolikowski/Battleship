#!/usr/bin/env bash

do_install() {
    if battleship_installed; then
	echo "Battleship already installed"
	return
    fi

    echo "Installing battleship"
    deep_clean
    
    /usr/bin/virtualenv venv2
    /usr/bin/virtualenv -p python3 venv3

    . venv2/bin/activate
    python setup.py install
    deactivate

    . venv3/bin/activate
    python setup.py install
    deactivate

    # Delete folders that were created during the install
    clean
}

battleship_installed() {
    if [ ! -d venv2 ] || [ ! -d venv3 ]; then
	echo -e "1Battleship is not installed! Run the following command:\n" \
             "$0 install" 
	return 1
    fi

    for i in venv2 venv3; do
	. $i/bin/activate
	if ! pip freeze | grep -q battleship; then
	    echo -e  "2Battleship is not installed! Run the following command:\n" \
		 "$0 install" 
	    return 1
	fi
	deactivate;
    done
}

clean() {
    rm -rf battleship.egg-info build dist
}

deep_clean() {
    clean
    rm -rf venv3 venv2
}

print_help() {
cat <<EOF
Please use one of the following options:
 local   - play a local game (against another player on same computer)
 gui     - play a GUI demo
 online  - play an online game (unstable!)

For example:
\$ $0 install"

Consult the documentation for more help:
https://bitbucket.org/cmors001/battleship/wiki/Home
EOF
}

if [ $1 == install ]; then
    do_install
    echo -e "\n\n\n"
    print_help
    exit
fi

if [ $1 == remove ]; then
    deep_clean
    exit
fi


case $1 in

    gui)
	# battleship_installed || exit 1
	# . venv2/bin/activate
	# src/pygame-gui.py
	# deactivate
	python2 src/pygame-gui.py
	;;
    local)
	# battleship_installed || exit 1
	# . venv3/bin/activate
	# src/text_frontend.py
	# deactivate
	python3 src/cursesFrontEnd.py
	;;
    online)
	# battleship_installed || exit 1
	# . venv3/bin/activate
	# src/text_frontend.py
	# deactivate
	python3 src/text_frontend.py
	;;
    *)
	print_help
	;;
esac
