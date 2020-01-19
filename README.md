# PosiKitty🐱

#### Keywords: Slack App, AWS Lambda, DynamoDB, AWS Comprehend

## Project description
People can get frustrated while working, and that results in negative language usage in the workspace. We want to make the work environment a bit more positive by reminding people to use a more neutral and positive tone when addressing negative comments

## System Architecture
Updating sentiment value:
Slack hook per message → AWS API gateway → AWS lambda → AWS Comprehend → AWS Dynamo saving sentiment score per user in the workspace → response with sentiment value → slack query giphy cat → slack bot send cat gif to user

## Limitations
AWS Comprehend API requires a language code input. We might be able to detect the input language using Google Cloud language detection API. We will likely support english only for now.

## Data Design
```
userid : [string]
sentiment {
  Mixed : [Decimal] 
  Neutral : [Decimal]
  Positive : [Decimal]
  Negative : [Decimal]
}
timestamp : [Decimal]
kitty_channel_id : [string]
```
