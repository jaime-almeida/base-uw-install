#!/bin/bash
cd  ~

echo "\n \n \n \n \n"
echo "        -------------------------------------------------------"
echo "        |                                                     |"
echo "        |              Installing dependencies                |"
echo "        |                                                     |"
echo "        -------------------------------------------------------"
echo "\n \n \n \n \n"

sudo apt-get update
sudo apt-get --assume-yes upgrade

sudo apt-get --assume-yes install unrar cmake fcc python-dev hdf5-tools libhdf5-serial-dev libhdf5-dev libhdf5-openmpi-dev
sudo apt-get --assume-yes install openmpi-bin openmpi-common openssh-client openssh-server libopenmpi1.10 libopenmpi-dev
sudo apt-get --assume-yes install libxml2-dev libpng-dev

echo "\n\n\n\n\n"

echo "        -------------------------------------------------------"
echo "        |                                                     |"
echo "        |          Dealing with installation files            |"
echo "        |                                                     |"
echo "        -------------------------------------------------------"

echo "\n\n\n\n\n"

cd base-uw-install*/petsc*
tar xzvf petsc-3.5.4.tar.gz; mv petsc-3.5.4 ~

cd ../uw\ zips
unrar x bleedingEdge.part01.rar
mkdir ~/uw
sudo mv bleedingEdge ~/uw

echo "\n\n\n\n\n"

echo "        -------------------------------------------------------"
echo "        |                                                     |"
echo "        |                  Configuring PETSc                  |"
echo "        |                                                     |"
echo "        -------------------------------------------------------"


echo "\n\n\n\n\n"
cd ~/petsc-*

./configure --with-mumps=1 --download-mumps=1 --with-scalapack=1 --download-scalapack=1 --with-blacs=1 --download-blacs=1 --download-fblaslapack=1 --download-metis=1 --with-parmetis=1 --download-parmetis --with-shared-libraries=1 --with-debugging=0 --with-pic=1


sudo make PETSC_DIR=/home/$USER/petsc-3.5.4 PETSC_ARCH=arch-linux2-c-opt all
make PETSC_DIR=/home/$USER/petsc-3.5.4 PETSC_ARCH=arch-linux2-c-opt test

# Deal with exportations and bash stuff
export PETSC_DIR=/home/$USER/petsc-3.5.4/
echo "export PETSC_DIR=/home/$USER/petsc-3.5.4/" >> ~/.bashrc

echo "\n\n\n\n\n"

echo "        -------------------------------------------------------"
echo "        |                                                     |"
echo "        |                Configuring Underworld               |"
echo "        |                                                     |"
echo "        -------------------------------------------------------"


echo "\n\n\n\n\n"

sudo chmod -R 777 ~/uw; cd ~/uw/bleedingEdge/

sudo ./configure.py --petsc-dir=$PETSC_DIR --hdf5-dir=/usr/lib/x86_64-linux-gnu/hdf5/openmpi

./scons.py

export UW_DIR=/home/$USER/uw/bleedingEdge/build/bin
echo "export UW_DIR=/home/$USER/uw/bleedingEdge/build/bin" >> ~/.bashrc

cd CartesianEarthbox
sudo ./configure.py --petsc-dir=$PETSC_DIR --hdf5-dir=/usr/lib/x86_64-linux-gnu/hdf5/openmpi
./scons.py
