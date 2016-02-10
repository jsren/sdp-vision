#!/bin/sh
echo "restoring v4lctl settings to previous values"
v4lctl setattr bright 255
echo "setting bright to 255"
v4lctl setattr contrast 127
echo "setting contrast to 127"
v4lctl setattr color 127
echo "setting color to 127"
v4lctl setattr hue 127
echo "setting hue to 127"
v4lctl setattr Red Balance 0
echo "setting Red Balance to 0"
v4lctl setattr Blue Balance 5
echo "setting Blue Balance to 5"
echo "v4lctl values restored"