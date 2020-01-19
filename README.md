#PosiKitty🐱

#Keywords: Slack App, AWS Lambda, DynamoDB, AWS Comprehend

##Project description
People can get frustrated while working, and that results in negative language usage in the workspace. We want to make the work environment a bit more positive by reminding people to use a more neutral and positive tone when addressing negative comments
System Architecture
Updating sentiment value:
Slack hook per message → AWS API gateway → AWS lambda → AWS Comprehend → AWS Dynamo saving sentiment score per user in the workspace → response with sentiment value → slack query giphy cat → slack bot send cat gif to user
Limitations
AWS Comprehend API requires a language code input. We might be able to detect the input language using Google Cloud language detection API. We will likely support english only for now.
Data Design

username/id
Datetime
Sentiment Grade



Video Story:

In a small Tech company, there are 3 main characters.

Manager: The product manager of the team
Colleague: Poor worker’s colleague, who was already in the team for years
Poor Worker:


Poor Worker: Sorry, I blew up our db.
Colleague: WTF? We have a release today!
Manager: Are you f****** kidding me?
