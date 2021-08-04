# Time Tracker CLI

Here you can find all the source code of the Time Tracker CLI. 
This is responsible for automatically generating fake data for the Cosmos emulator, 
in order to have information when testing new features or correcting bugs.

> This feature is only available in development mode.  

## Prerequisites

- Backend and cosmos emulator containers up.
- Environment variables correctly configured

### Environment Variables.

The main environment variables that you need to take into account are the following:

```shell
export DATABASE_ACCOUNT_URI=https://azurecosmosemulator:8081
export DATABASE_MASTER_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
export DATABASE_NAME=time_tracker_testing_database
```
Verify that the variables are the same as those shown above. 

## How to use Time Tracker CLI?

If we are in the project's root folder, we need to redirect to the folder `cosmosdb_emulator` and open a terminal.

We have two main alternatives for running the CLI:

### Execute CLI with flags.
   
In order to see all the available flags for the CLI we are going to execute the following command:

```shell
./cli.sh main.py --help
```

When executing the above command, the following information will be displayed:

![image](https://user-images.githubusercontent.com/56373098/127604274-041c2af7-d7a8-4b8d-b784-8280773b68c8.png)

Where you can see the actions we can perform on a given Entity:

Currently, the CLI only allows the creation of Time-entries and allows the deletion of any entity.

Available Actions:

- Create: Allows creating new fake data about a certain entity.
- Delete: Allows creating cosmos data about a certain entity.

> To delete information about a certain entity you have to take into account the relationship 
that this entity has with other entities, since this related information will also be eliminated, 
for this purpose the following diagram can be used as a reference:
![image](https://user-images.githubusercontent.com/56373098/127604828-77cc1f90-21d4-4c63-9881-9d6546d84445.png)

Available Entities:

- Customers
- Projects
- Project-Types
- Activities
- Time-entries

Considering the actions that we can execute on the entities we can perform the following command 
to generate entries:
```shell
./cli.sh main.py -a Create -e Time-entries
```

The result of this command will be as follows:

![image](https://user-images.githubusercontent.com/56373098/127606245-6cb5a0d1-ada6-4194-bbeb-6bd9679b676b.png) 

In this way we can continue with the generation of entities in an interactive way.
    
### Execute CLI in an interactive way

To run the CLI interactively, we need to execute the following command:

```shell
./cli.sh main.py
```
After executing the above command, the following will be displayed:

![image](https://user-images.githubusercontent.com/56373098/127606606-422c6841-bd40-4f36-be2e-e765d333beed.png)

This way we can interact dynamically with the CLI for the generation/deletion of entities.

> Currently, for the generation of personal entries it is necessary to know the identifier of our user within Time Tracker. 