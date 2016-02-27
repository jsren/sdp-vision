#!/bin/sh
echo "restoring v4lctl settings to previous values"
v4lctl setattr bright 180
echo "setting bright to 180"
v4lctl setattr contrast 121
echo "setting contrast to 121"
v4lctl setattr color 83
echo "setting color to 83"
v4lctl setattr hue 5
echo "setting hue to 5"
v4lctl setattr Red Balance 5
echo "setting Red Balance to 5"
v4lctl setattr Blue Balance 0
echo "setting Blue Balance to 0"
echo "v4lctl values restored"