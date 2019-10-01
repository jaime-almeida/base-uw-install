#!/bin/bash
cd  ~

echo "\n \n \n \n \n"
echo "-------------------------------------------------------"
echo "|                                                     |"
echo "|              Installing dependencies                |"
echo "|                                                     |"
echo "-------------------------------------------------------"
echo "\n \n \n \n \n"

sudo apt-get update
sudo apt-get --assume-yes upgrade

sudo apt-get --assume-yes install unrar cmake fcc python-dev hdf5-tools libhdf5-serial-dev libhdf5-dev
sudo apt-get --assume-yes install openmpi-bin openmpi-common openssh-client openssh-server libopenmpi1.10 libopenmpi-dev
sudo apt-get --assume-yes install libxml2-dev libpng-dev

echo "-------------------------------------------------------"
echo "|                                                     |"
echo "|          Dealing with installation files            |"
echo "|                                                     |"
echo "-------------------------------------------------------"

echo "\n\n\n\n\n"

cd base-uw-install*/petsc*
tar xzvf petsc-3.5.4.tar.gz; mv petsc-3.5.4 ~

cd ../uw\ zips
unrar -x bleedingEdge.part01.rar
mkdir ~/uw
mv bleedingEdge ~/uw

echo "-------------------------------------------------------"
echo "|                                                     |"
echo "|                  Configuring PETSc                  |"
echo "|                                                     |"
echo "-------------------------------------------------------"


echo "\n\n\n\n\n"
cd ~/petsc-*

./configure --with-mumps=1 --download-mumps=1 --with-scalapack=1 --download-scalapack=1 --with-blacs=1 --download-blacs=1 --download-fblaslapack=1 --download-metis=1 --with-parmetis=1 --download-parmetis --with-shared-libraries=1 --with-debugging=0 --with-pic=1

