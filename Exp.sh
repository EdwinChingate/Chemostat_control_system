echo Which reactor do you wanna start?
echo 1
echo 2
echo 3
echo 4
echo 5
echo 6
echo 7
echo 8
echo 9
echo 10
read reactor
while true
echo yes
do
if [ "$reactor" -gt "0" ] && [ "$reactor" -lt "11" ]
then 
clear
break
else
echo Which reactor do you wanna start?
echo 1
echo 2
echo 3
echo 4
echo 5
echo 6
echo 7
echo 8
echo 9
echo 10
read reactor
fi
sleep 5
clear
done
echo new?: y
read new
if [ "$new" = "y" ]
then 
echo start new reactor
echo $reactor | python3 start.py
else 
echo restart reactor
echo $reactor | python3 restart.py
fi
read test < ${reactor}.txt
cd $test
while true;
do
sleep 10
echo $reactor | python3 Experiment${reactor}.py
echo $reactor | python3 stop.py 
sleep 10
done
