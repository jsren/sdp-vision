#!/bin/sh
echo "restoring v4lctl settings to previous values"
v4lctl setattr bright 150
echo "setting bright to 150"
v4lctl setattr contrast 103
echo "setting contrast to 103"
v4lctl setattr color 67
echo "setting color to 67"
v4lctl setattr hue 0
echo "setting hue to 0"
v4lctl setattr Red Balance 5
echo "setting Red Balance to 5"
v4lctl setattr Blue Balance 0
echo "setting Blue Balance to 0"
echo "v4lctl values restored"