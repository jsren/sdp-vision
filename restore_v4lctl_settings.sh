#!/bin/sh
echo "restoring v4lctl settings to previous values"
v4lctl setattr bright 23296
echo "setting bright to 23296"
v4lctl setattr contrast 28416
echo "setting contrast to 28416"
v4lctl setattr color 65408
echo "setting color to 65408"
v4lctl setattr hue 38144
echo "setting hue to 38144"
echo "v4lctl values restored"