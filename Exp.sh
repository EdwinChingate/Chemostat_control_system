echo Which reactor do you wanna start?
#Approve
echo Blue: 0
echo Black: 1
echo Purple: 2
echo Green: 3
echo Orange: 4
echo Red: 5
read reactor
while true
echo yes
do
if [ "$reactor" -gt "-1" ] && [ "$reactor" -lt "6" ]
then 
clear
break
else
echo Which reactor do you wanna start?
echo Blue: 0
echo Black: 1
echo Purple: 2
echo Green: 3
echo Orange: 4
echo Red: 5
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
