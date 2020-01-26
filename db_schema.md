# Database schema

## memes

| field       | type | additional |
| ----------- | ---- | ---------- |
| question_id | int  | unique     |

## site

| field          | type | additional |
| -------------- | ---- | ---------- |
| meme_id        | int  | unique     |
| meme_name      | text |            |
| blacklisted    | bool |            |
| include_random | bool |            |
