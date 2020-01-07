# TeamBuilder
TeamBuilder is a website intended for use by coordinators of teamwork-based activities. It provides a simpler way to automatically generate  teams, whilst allowing customizable constraints on team makeup. This repository is a fork of [aidanstansfield/DECO3801Project](https://github.com/aidanstansfield/DECO3801Project) (technically not a fork since GitHub doesn't allow forks of one's own repos)

## Deployment
Detailed information about how to setup and deploy TeamBuilder can be found in [setup.txt](doc/setup.txt)

## Surveys
In order to collect the information needed for an allocation, TeamBuilder allows the coordinator to create and send surveys to their students. These surveys can contain a variety of different questions, and a link to the survey will then be emailed to student email accounts. 

## Allocation
In order to perform allocation, TeamBuilder makes use of the [simulated annealing](https://en.wikipedia.org/wiki/Simulated_annealing) optimisation strategy, via the required [simanneal](https://pypi.org/project/simanneal/) library.

