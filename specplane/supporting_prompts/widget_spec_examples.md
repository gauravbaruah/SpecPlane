# IMPORTANT

- the first prompt should always be the specplane schema prompt from the core_prompt folder
- we can then follow up with generating specs for a module or component, or for validation of the specs

# Login widget spec generation prompt

OK... let's try to make specifications for a login_widget given the instructions you have in this chat's context. You can also refer to `{core_prompt_file}` as needed.

I want you to draft `specs/{login_widget}.yaml` in the specplane schema with the following requirements:
- support for oauth by Google and Apple id
- a message saying we'll only access your profile picture, and email address from Google/Apple when using oauth
- the backend is firebase firestore collection called users
- once the oauth flow is done we want the onboarding screen to pop up (TBD)
- appropriate failure cases tracked and messaging displayed on the the login screen as needed.


# Input Prompt to create onboarding screen spec

Let's add the onboarding screen. 

we want:
- to ask the user to enter their first name ("What should we call you?")
  - this is a mandatory requirement and will be added to the user profile
- ask the user for mic permissions with a message saying we support dictation of you notes and instructions using your voice.
- if the user skips the mic permisions, we may need to ask for it again at a later stage (if the user clicks on any control)
  - hmm... this may need a mic permission asker/accepter widget.
- once onboarding is complete we want to navigate to the dashboard

Note:
- we only want to ask for onboarding once after logging in.
- the user if onboarded can move directly to the dashboard

