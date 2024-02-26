# Decentralized Authentication

## Provision Cognito User Group

Using the AWS Console we'll create a Cognito User Group

- Go to Amazon Cognito and create a user pool
  - Provider types: Cognito user pool
  - Cognito user pool sign-in options: Email
  - Password policy mode: Cognito defaults
  - MFA enforcement: No MFA
  - Check Enable self-service account recovery
  - Delivery method for user account recovery messages: Email only
  - Check Enable self-registration
  - Check Allow Cognito to automatically send messages to verify and confirm
  - Attributes to verify: Send email message, verify email address
  - Check Keep original attribute value active when an update is pending
  - Active attribute values when an update is pending: Check Email address
  - Additional required attributes: Select 'name' and 'preferred_username'
  - Email provider: Send email with Cognito
  - User pool name: cruddur-user-pool
  - App type: Public client
  - App client name: cruddur
  - Client secret: Don't generate a client secret
  - Review and create user pool

## Install AWS Amplify

- See documentation: https://docs.amplify.aws/react/build-a-backend/auth/

```sh
cd frontend-react-js
```

```sh
npm i aws-amplify --save
```

- This adds `aws-amplify` to `package.json` and modifies `package-lock.json`

## Configure Amplify

We need to hook up our cognito pool to our code in the `App.js`

```js
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_identity_pool_id": process.env.REACT_APP_AWS_COGNITO_IDENTITY_POOL_ID, //Remove this as we are not using identity pool
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```

- Go to `docker-compose.yml` and configure the following as environment variables for frontend-react-js

```
REACT_APP_AWS_PROJECT_REGION
REACT_APP_AWS_COGNITO_REGION
REACT_APP_AWS_USER_POOLS_ID
REACT_APP_CLIENT_ID
```

## Conditionally show components based on logged in or logged out

Inside our `HomeFeedPage.js`

```js
import { Auth } from 'aws-amplify';

// set a state
const [user, setUser] = React.useState(null);

// check if we are authenicated
const checkAuth = async () => {
  Auth.currentAuthenticatedUser({
    // Optional, By default is false. 
    // If set to true, this call will send a 
    // request to Cognito to get the latest user data
    bypassCache: false 
  })
  .then((user) => {
    console.log('user',user);
    return Auth.currentAuthenticatedUser()
  }).then((cognito_user) => {
      setUser({
        display_name: cognito_user.attributes.name,
        handle: cognito_user.attributes.preferred_username
      })
  })
  .catch((err) => console.log(err));
};

// check when the page loads if we are authenicated
React.useEffect(()=>{
  loadData();
  checkAuth();
}, [])
```

We'll want to pass user to the following components:

```js
<DesktopNavigation user={user} active={'home'} setPopped={setPopped} />
<DesktopSidebar user={user} />
```

We'll rewrite `DesktopNavigation.js` so that it it conditionally shows links in the left hand column
on whether you are logged in or not.

Notice we are passing the user to ProfileInfo

```js
import './DesktopNavigation.css';
import {ReactComponent as Logo} from './svg/logo.svg';
import DesktopNavigationLink from '../components/DesktopNavigationLink';
import CrudButton from '../components/CrudButton';
import ProfileInfo from '../components/ProfileInfo';

export default function DesktopNavigation(props) {

  let button;
  let profile;
  let notificationsLink;
  let messagesLink;
  let profileLink;
  if (props.user) {
    button = <CrudButton setPopped={props.setPopped} />;
    profile = <ProfileInfo user={props.user} />;
    notificationsLink = <DesktopNavigationLink 
      url="/notifications" 
      name="Notifications" 
      handle="notifications" 
      active={props.active} />;
    messagesLink = <DesktopNavigationLink 
      url="/messages"
      name="Messages"
      handle="messages" 
      active={props.active} />
    profileLink = <DesktopNavigationLink 
      url="/@andrewbrown" 
      name="Profile"
      handle="profile"
      active={props.active} />
  }

  return (
    <nav>
      <Logo className='logo' />
      <DesktopNavigationLink url="/" 
        name="Home"
        handle="home"
        active={props.active} />
      {notificationsLink}
      {messagesLink}
      {profileLink}
      <DesktopNavigationLink url="/#" 
        name="More" 
        handle="more"
        active={props.active} />
      {button}
      {profile}
    </nav>
  );
}
```

We'll update `ProfileInfo.js`

```js
import { Auth } from 'aws-amplify';

const signOut = async () => {
  try {
      await Auth.signOut({ global: true });
      window.location.href = "/"
  } catch (error) {
      console.log('error signing out: ', error);
  }
}
```

We'll rewrite `DesktopSidebar.js` so that it conditionally shows components in case you are logged in or not.

```js
import './DesktopSidebar.css';
import Search from '../components/Search';
import TrendingSection from '../components/TrendingsSection'
import SuggestedUsersSection from '../components/SuggestedUsersSection'
import JoinSection from '../components/JoinSection'

export default function DesktopSidebar(props) {
  const trendings = [
    {"hashtag": "100DaysOfCloud", "count": 2053 },
    {"hashtag": "CloudProject", "count": 8253 },
    {"hashtag": "AWS", "count": 9053 },
    {"hashtag": "FreeWillyReboot", "count": 7753 }
  ]

  const users = [
    {"display_name": "Andrew Brown", "handle": "andrewbrown"}
  ]

  let trending;
  if (props.user) {
    trending = <TrendingSection trendings={trendings} />
  }

  let suggested;
  if (props.user) {
    suggested = <SuggestedUsersSection users={users} />
  }
  let join;
  if (props.user) {
  } else {
    join = <JoinSection />
  }

  return (
    <section>
      <Search />
      {trending}
      {suggested}
      {join}
      <footer>
        <a href="#">About</a>
        <a href="#">Terms of Service</a>
        <a href="#">Privacy Policy</a>
      </footer>
    </section>
  );
}
```

## Modify Signin Page

```js
import { Auth } from 'aws-amplify';

  const [errors, setErrors] = React.useState('');

  const onsubmit = async (event) => {
    setErrors('')
    event.preventDefault();
    Auth.signIn(email, password)
    .then(user => {
      console.log('user',user)
      localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
      window.location.href = "/"
    })
    .catch(error => { 
      if (error.code == 'UserNotConfirmedException') {
        window.location.href = "/confirm"
      }
      setErrors(error.message)
    });
    return false
  }

  let el_errors;
  if (errors){
    el_errors = <div className='errors'>{errors}</div>;
  }

// just before submit component
{el_errors}
```

- Try to sign in to get an unauthorized (username and password error) error

- You can try to manually create a user on the AWS cognito console (you should get an email from cognito to verify that user) and sign in with the user details

- If it requires force-change-password, you can run this command on the cli to bypass
```sh
aws cognito-idp admin-set-user-password --username andrewbrown --password Testing1234! --user-pool-id us-east-2_xMATXNbsI --permanent
```
- Try to inspect the crudder homepage after signin to see ![inspect1]() ![inspect2]()

- Go to cognito console and manually enter required attributes (name and prefered username). Then refresh cruddur to confirm.

- After confirmation, delete the manually created user from cognito and sign out from cruddur


## Modify Signup Page

```js
import { Auth } from 'aws-amplify';

const [cognitoErrors, setCognitoErrors] = React.useState('');

const onsubmit = async (event) => {
  event.preventDefault();
  setCognitoErrors('')
  try {
      const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
            name: name,
            email: email,
            preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
            enabled: true,
        }
      });
      console.log(user);
      window.location.href = `/confirm?email=${email}`
  } catch (error) {
      console.log(error);
      setCognitoErrors(error.message)
  }
  return false
}

let errors;
if (cognitoErrors){
  errors = <div className='errors'>{cognitoErrors}</div>;
}

//before submit component
{errors}
```

## Modify Confirmation Page

```js
import { Auth } from 'aws-amplify';

const resend_code = async (event) => {
  setCognitoErrors('')
  try {
    await Auth.resendSignUp(email);
    console.log('code resent successfully');
    setCodeSent(true)
  } catch (err) {
    // does not return a code
    // does cognito always return english
    // for this to be an okay match?
    console.log(err)
    if (err.message == 'Username cannot be empty'){
      setCognitoErrors("You need to provide an email in order to send Resend Activiation Code")   
    } else if (err.message == "Username/client id combination not found."){
      setCognitoErrors("Email is invalid or cannot be found.")   
    }
  }
}

const onsubmit = async (event) => {
  event.preventDefault();
  setCognitoErrors('')
  try {
    await Auth.confirmSignUp(email, code);
    window.location.href = "/"
  } catch (error) {
    setCognitoErrors(error.message)
  }
  return false
}
```
- Try signing up on cruddur frontend
- This should give you a confirm email page. Also go to cognito userpool under users to see that it is waiting for confirmation.
- Check you email for verification code and confirm. On the cognito console, you will also see that it is confirmed.
- Now, it requires signin after verification so sign-in on cruddur

+ Also, test resend verification code option

## Setup Recovery Page

```js
import { Auth } from 'aws-amplify';

const onsubmit_send_code = async (event) => {
  event.preventDefault();
  setCognitoErrors('')
  Auth.forgotPassword(username)
  .then((data) => setFormState('confirm_code') )
  .catch((err) => setCognitoErrors(err.message) );
  return false
}

const onsubmit_confirm_code = async (event) => {
  event.preventDefault();
  setCognitoErrors('')
  if (password == passwordAgain){
    Auth.forgotPasswordSubmit(username, code, password)
    .then((data) => setFormState('success'))
    .catch((err) => setCognitoErrors(err.message) );
  } else {
    setCognitoErrors('Passwords do not match')
  }
  return false
}

- Try to use the forget password option at signin
- Check email for password reset code
- Enter reset code and new password. Then proceed to signin.


## Backend Implementation for Cognito
## Authenticating Server Side

Add in the `HomeFeedPage.js` a header to pass along the access token

```js
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
  }
```

In the `app.py`

```py
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
```

- You can confirm from the backend logs that the access token is being passed along by viewing it with debug. 
- Edit the @app.route("/api/activities/home", methods=['GET']) section like this:

```py
@app.route("/api/activities/home", methods=['GET'])
def data_home():
  app.logger.debug("AUTH HEADER")
  app.logger.debug(
    request.headers.get('Authorization')
  )
  data = HomeActivities.run(logger=LOGGER)
  return data, 200
```

- Make sure to remove the debug after confirming

+ Now, we need to instrument for server side verification of the json web token (jwt) generated

- Add `Flask-AWSCognito` to requirements.txt

- `cd` into backend-flask and do `pip install -r requirements.txt`

- From the instructions (https://github.com/cgauge/Flask-AWSCognito), we need to set the following env variables in backend-flask of docker-compose

```yml
AWS_COGNITO_USER_POOL_ID: "us-east-2_xMATXNbsI"
AWS_COGNITO_USER_POOL_CLIENT_ID: "6lii3ennqt31pr8a1clgihnmbc"
```

- In backeend-flask, creat a folder named _lib_

- Next, create a file `cognito_jwt_token.py`. Paste code from https://github.com/cgauge/Flask-AWSCognito/blob/master/flask_awscognito/services/token_service.py and edit appropriately

- In _app.py_, instrument the cognito_jwt_token.py module

- Also edit _home_activities.py_ and _ProfileInfo.js_

- Sign into cruddur and view docker-compose backend logs to confirm authentication

- On cruddur, a certain section was added as mockup for only authenticated users and shouldn't be seen when signed out.