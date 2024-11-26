# Causally Consistent Database
This is a simple demonstration of causally consistent databases where time.sleep was used to simulate the geographic separation that could cause inconsistencies. In the demo, there is one users and two databases. The user says that they lost their wedding ring, then they say they found it. The first message is delayed, and the second message is dependent upon the first. If the second message is recorded by the other database before the first message, it would be causally inconsisent. This is program shows how dependencies can be checked to ensure causal consistency.

## How To Use It:

**Tech used:** Python, MySQL

You will need to install mysql-connector-python as show in the dependencies file. 
Additionaly, a configvals.py file must be created to store the login credentials for the MySQL database instance you are using.
To set up the tables, run the create_db.sql script.

## Optimizations

Originally, all of the messages and dependencies were stored in dictionaries. I have recently returned to this project to move that data onto a local MySQL database. Admitedly, it is using a brute force method to check for dependencies that would not scale on a highly active system. In the future, I plan to use Lamport's Clock and remove old dependencies to optimize that process.

## Lessons Learned:

- Be careful when making queries with multithreading. If 2 threads make a query on the same connection, it disconnects. I considered using pooling, but I realized this issue only came with replicating writes. Since the demo is simplistic and does not open many threads I opted to simply open a new connection when replicating writes and close it when the replication is complete.
- Invest time in creating tools to help you in the debugging process. Creating the clear_databases.py script didn't take long but made life so much easier. Having a demo script to create inputs for you automatically is also extremeley helpful.
- Do not look over any changes you made when debugging. There were a few times during this project where I made a small changed, and I was confident it would not cause any bugs. I would then continue to make large changes and when the program stopped working, I assumed it was because of those recent large changes I made. In reality, it was the small tweak from before that I forgot about, and it cause me much more time than it would have if I had taken a minute to test the script. 