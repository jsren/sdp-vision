#!/bin/sh
echo "restoring v4lctl settings to previous values"
v4lctl setattr bright 160
echo "setting bright to 160"
v4lctl setattr contrast 110
echo "setting contrast to 110"
v4lctl setattr color 100
echo "setting color to 100"
v4lctl setattr hue 0
echo "setting hue to 0"
echo "v4lctl values restored"