# AudioPin: AI-driven podcast knowledge capture App

**AudioPin** provides a solution by allowing users to effortlessly record audio snippets and attach personalized notes for context, creating a powerful system to retain and organize knowledge from podcasts. The app is cross-platform, ensuring users can enjoy a consistent experience on both iOS and Android devices. With AudioPin, podcast listeners can easily revisit their favorite moments and take their learning to the next level.

## Repository

Frontend repository: https://github.com/xosadmin/cits5206-frontend

Backend repository: https://github.com/xosadmin/cits5206-backend 

## Features

**1. Signup/Login**

- User authentication functionality that allows users to create accounts or log in to the app.

**2. Default Podcast Categories**

- Displays default categories of podcasts on the homepage for easy navigation and discovery.

**3. Search for Podcasts**

- A search functionality that enables users to find podcasts based on keywords, categories, or other filters.

**4. Mini Player**

- A mini player that allows users to control playback without leaving the current screen.

**5. Audio Snippet Capture**

- Allows users to capture specific segments of a podcast audio for future reference.

**6. Make a note**

- Provides users with the ability to attach notes to audio snippets for contextual organization.

**7. Podcast Player**

- A full-featured podcast player for listening to and controlling podcast playback.

## Key Features:

### 1. **Sleep Timer**

The Sleep Timer functionality allows users to set a specific time for the podcast to automatically stop playing. Users can select predefined timers (e.g., 15, 30, 60 minutes) or set a custom duration.

- **Predefined Options**: 15, 30, 45, or 60 minutes.
- **Custom Timer**: Users can manually set a custom sleep duration.
- **Automatic Stop**: Playback will automatically pause after the timer expires.

### 2. **Playback Speed Control**

The podcast player supports speed adjustment, allowing users to listen at their desired pace without compromising the audio quality.

- **Speed Options**: 0.5x, 1x, 1.25x, 1.5x, 2x.
- **Seamless Transitions**: Changes in speed occur smoothly, without affecting the flow of playback.

### 3. **Sleek Seeker and Playback Controls**

The player includes intuitive playback controls to navigate through podcasts effortlessly.

- **Seek Bar**: Allows for precise navigation to any part of the episode.
- **Forward/Backward Skip**: Jump 10 seconds forward or backward for quick navigation.
- **Play/Pause**: Simple toggles for control.

### 4. **Queue Reordering**

This feature allows users to reorder episodes in their current playlist or queue, offering flexibility in how they listen to content.

- **Drag-and-Drop**: Episodes can be rearranged by dragging them into the desired order.
- **Add/Remove Episodes**: Users can manage the queue by adding or removing episodes easily.

### 5. **Clipping and Transcription**

This feature allows users to capture and transcribe short audio snippets from podcasts.

- **Clip Button**: A simple button in the player allows users to create 10-second audio clips.
- **Automatic Transcription**: When a clip is created, Google Cloud’s speech-to-text is used to generate a transcription for the selected 10-second audio segment.
- **Edit Transcriptions**: The transcribed text can be edited by users for accuracy or clarification.

### 6. **Rich Text Editor for Pins**

Users can capture important moments by pinning sections of the podcast and adding rich text notes for later reference.

- **Pin Important Moments**: Users can add pins at key timestamps while listening.
- **Rich Text Editing**: Add headers, bullet points, and links to notes, using markdown support.
- **Save Pins**: Pins are saved in JSON format for easy exporting and sharing.

## Frontend Setup Preperation

Before starting, please ensure your system meets the following requirements:

- Operating System: macOS or Windows
- Flutter SDK: Flutter 3.0.0 or above
- Dart SDK: Included with the Flutter SDK

## Installation

### **Step 1. Install Flutter SDK**

1. Visit the [Flutter website](https://docs.flutter.dev/).

2. Choose the installation package based on your operating system and follow the instructions in the documentation.

3. Configure the environment variables:

macOS:

```bash
export PATH="$PATH:`flutter_path`/bin"
```

Windows: Add the bin directory of Flutter to your system's PATH.

4. Verify the installation by running:

```bash
flutter doctor
```

This command will check if all dependencies are correctly installed.

### **Step 2. Install Development Tools**

1. iOS Environment:

- Install Xcode and configure the command-line tools:

```bash
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
```

- Ensure CocoaPods is installed:

```bash
sudo gem install cocoapods
```

2. Android Environment:

- Install Android Studio and ensure the Flutter and Dart plugins are installed.

- Configure the Android SDK path, and make sure the required virtual devices are enabled for debugging.

### **Step 3. Initialize the Project**

1. Clone the project repository and enter the directory:

```bash
git clone <https://github.com/xosadmin/cits5206-frontend>
```

```bash
cd <project-directory> // you can modify the directory's name once you downloaded it from the Github
```

2. Install project dependencies:

```bash
flutter pub get
```

## **Run the Project**

- Running on iOS Simulator:

1. Open Xcode and select the iOS simulator from the project.

2. Run the following command to start the iOS simulator and compile the app:

```bash
flutter run
```

- Running on Android Emulator:

1. Open Android Studio and start the virtual device.

2. Use the following command to launch the project:

```bash
flutter run
```

## Backend Deployment

### System Requirement

To run the backend server smoothly, the following system configuration is essential:

- CPU: x86-64 / x86 (recommend with no less than 2 cores)
- RAM: 2GB (4GB is recommended if more requests will be handled)
- Disk: 20GB
- Operating System (OS): Linux (Debian 12+ (BullSeye), Almalinux 9+, Ubuntu 24.04+)

Note: it is possible to run the backend server within hypervisors (including LXC, XEN, KVM, etc.). If the client is trying to run the server on OpenVZ™ 7 with Docker, the privileges must be given before install Docker engine. **OpenVZ version 6** is **not supported with Docke and unrecommended** as it is EOL.

### System Dependencies

The backend server is relying on following dependencies:

- MySQL™ / MariaDB ① (recommended)
- Python™ 3.6+ with `pip and venv`
- DoveCot and PostFix ② (Not just these two, all mail servers with SMTP/POP3 are supported)

① The MySQL/MariaDB could be hosted separately. Please make sure specified the DB connection information in conf.ini correctly.

② The DoveCot and PostFix could be hosted separately. Please note that you need to **contact your upstream Internet Service Provider (ISP) to whitelist SMTP ports (like 25, 465, etc.) outgoing and ingoing**. It is also required to specify connection information in `conf.ini`.

### Method 1: Using Docker

This is the easiest way to deploy the backend server using Docker. The Dockerfile is provided. The customer could compile the image and run the image based on the following guidelines.

The method below is assumed Docker container is installed, and the backend server files are downloaded on the host machine.

**Running MariaDB within Docker**

1.  Create data directory

2.  Using following command to run the MariaDB database server: `docker run --name some-mysql -v /path/to/datadir:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql`

3.  Install MySQL Client on host machine:

- On RedHat/CentOS/Almalinux/RockyLinux/Fedora: `dnf install mariadb -y`
- On Debian/Ubuntu: `apt install mariadb -y`

Note: it is highly **UNRECOMMENDED** to set True MySQL Root Password within command line.

**Running Dovecot within docker**

- Do custom configuration for Dovecot based on [official guideline](https://hub.docker.com/r/dovecot/dovecot)
- Running Dovecot using the command: `docker run -d –name dovecot -v /path/to/custom/config: /etc/dovecot/conf.d -v /path/to/save/email:/srv/mail dovecot/dovecot`

Note: The image comes with default configuration which accepts any user with password `pass` by default. It is **HIGHLY RECOMMENDED** to do **custom configuration** to **ensure security** and avoid from brute-force attack.

**Compile image and run the image**

- Navigate to backend server file folder
- Use `docker build -t foo .`, where foo is your image name
- Create a new container by the following command: `docker run -d -p 5000:5000 -v /path/to/your/app:/app foo`

Then, you can use following command to run the container:

`docker run -d --restart=always -p 8000:8000 cits5206-backend`

Once it run, the docker will automatically fetch all necessary dependencies and run the uWSGI server. The first run may take longer time because of it.

The container will listen to `8000/tcp` port on server. You could use reverse proxy server or WAF firewall like `Nginx` to do reverse proxy.

### Method 2: Host manually

The method below is assumed the backend server files are downloaded on the host machine.

- Clone the project to server.
- Install MariaDB server via following steps:

- On RedHat/CentOS/Almalinux/RockyLinux/Fedora: `dnf install mariadb mariadb-server -y`

- On Debian/Ubuntu: `apt install mariadb mariadb-server -y`

- Run MySQL Secure installation: `mysql_secure_installation`
- Install DoveCot server:

- On RedHat/CentOS/Almalinux/RockyLinux/Fedora: `dnf install dovecot -y`

- On Debian/Ubuntu: `apt install dovecot -y`

- Do configuration and run the DoveCot Server
- Navigate to root folder of the backend server.
- Update DB connection information and SMTP mail server connection information in `conf.ini`
- Use following command to run uWSGI server: `uwsgi --http :5000 --wsgi-file app.py --callable app`

Based on the steps above, the program is running and listening on port `5000/tcp`. You can use reverse proxy or WAF firewall (like `Nginx`) to do reverse proxy.

Also, it is highly **recommended** to encapsulate the run uWSGI server command as a system service, or use background methods to run it with system boots (e.g. `nohup`).

## API Routes Documentation

Here are all API routes including Request Method, Description, Required parameter(s) and Expected Return.

| API Route | Method | Description | Required Data | Expected Return Return |
| --- | --- | --- | --- | --- |
| `/` | GET | Returns a status message for unspecified commands. | None | `{ "Status": False, "Detailed Info": "No specified command." }` |
| `/login` | POST | Authenticates a user and returns a token. | `username`: String, `password`: String | `{ "Status": True, "Token": "<token>" }` |
| `/register` | POST | Registers a new user. | `username`: String, `password`: String | `{ "Status": True, "userID": "<userID>" }` |
| `/setuserinfo` | POST | Updates user information. | `userID`: String, `firstname`: String, `lastname`: String, `dob`: String | `{ "Status": True, "userID": "<userID>" }` |
| `/setuserinterest` | POST | Sets user interests. | `userID`: String, `interests`: String (comma-separated interest IDs) | `{ "Status": True, "Detailed Info": "User interests updated successfully" }` |
| `/changepass` | POST | Changes the user's password. | `tokenID`: String, `password`: String | `{ "Status": True, "userID": "<userID>" }` |
| `/addsnippet` | POST | Adds a snippet for a podcast. | `tokenID`: String, `content`: String, `podid`: String | `{ "Status": True, "SnippetID": "<snippetID>" }` |
| `/addnote` | POST | Adds a note for a podcast. | `tokenID`: String, `content`: String, `podid`: String | `{ "Status": True, "noteID": "<noteID>" }` |
| `/listnotes` | POST | Lists all notes for the authenticated user. | `tokenID`: String | `[{ "NoteID": "<noteID>", "PodcastID": "<podID>", "DateCreated": "<date>" }]` |
| `/notedetails` | POST | Retrieves the details of a specific note. | `tokenID`: String, `noteID`: String | `{ "NoteID": "<noteID>", "PodcastID": "<podID>", "Content": "<content>", "DateCreated": "<date>" }` |
| `/search` | POST | Searches for podcasts by name. | `tokenID`: String, `query`: String | `[{ "PodcastID": "<podID>", "PodcastName": "<podName>", "PodcastURL": "<podUrl>" }]` |
| `/listsubscription` | POST | Lists all subscriptions for the authenticated user. | `tokenID`: String | `[{ "Title": "<title>", "rssUrl": "<rssUrl>", "Date": "<date>" }]` |
| `/uploadopml` | POST | Uploads an OPML file to add subscriptions. | `userID`: String, `file`: OPML file | `{ "subscriptions": [{ "title": "<title>", "xmlurl": "<rssUrl>" }] }` |
| `/listcategory` | POST | Lists all podcast categories. | `tokenID`: String | `[{ "CategoryID": "<categoryID>", "categoryName": "<categoryName>" }]` |
| `/addpodcast` | POST | Adds a new podcast. | `tokenID`: String, `podName`: String, `categoryID`: String, `file`: MP3 file | `{ "Status": True, "PodcastID": "<podcastID>" }` |
| `/deletepodcast` | POST | Deletes a podcast by ID. | `tokenID`: String, `podID`: String | `{ "Status": True }` |
| `/deletenote` | POST | Deletes a note by ID. | `tokenID`: String, `noteID`: String | `{ "Status": True }` |
| `/deletesnippet` | POST | Deletes a snippet by ID. | `tokenID`: String, `snippetID`: String | `{ "Status": True }` |
| `/uploadvoicenote` | POST | Uploads a voice note. | `tokenID`: String, `file`: MP3 file | `{ "Status": True, "Detailed Info": "File successfully uploaded" }` |
| `/resetpasswordmail` | POST | Sends a password reset email. | `username`: String | `{ "Status": True, "Detailed Info": "Reset Password Mail Sent" }` |
| `/confirmreset/<token>` | GET | Confirms password reset using a token. | `token`: String | `{ "Status": True, "Detailed Info": "Password reset." }` |

## External APIs Used

**1. Podcast Index API**

This API is used to fetch live podcast data from various sources and integrate it into the app. The podcasts retrieved through this API are then played using the in-app podcast player, providing users with access to up-to-date content.

**2. Google Cloud Speech-to-Text V1 API**

This API is employed to convert audio snippets captured by users into text. The converted text is stored as notes, allowing users to reference their highlighted moments in podcasts efficiently.

## About the Developers

| Student Number | Student Name | Role | Github Account |
| --- | --- | --- | --- |
| 23877677 | Chen Shen | Backend | jerryshenfewcher |
| 23877962 | Jikang Song | Backend | jikang1116 |
| 23885505 | Hanxun Xu | Backend | xosadmin |
| 23904899 | Wendy Wang | Frontend | akikodesu |
| 23825634 | Yunwei Zhang | Frontend | Yunwei-Zhang |
| 23876142 | Nishanth Arul | Frontend | NishanthAru |

## Meeting Minutes

[Final product delivery meeting minute](https://docs.google.com/document/d/1U_4BgaqnUlw2fgXUFVB3IgS6ZU0utaC-/edit?usp=sharing&ouid=102112286274771703828&rtpof=true&sd=true)

[Other meeting minutes](https://drive.google.com/drive/folders/1XMT0iyp1JuL5kh2uiDmLoKDj2JgPwfMI?usp=sharing)

## References

- [Flutter Official Documentation](https://docs.flutter.dev/)
- [iOS Development Guide](https://docs.flutter.dev/get-started/install/macos/mobile-ios)
- [Android Development Guide](https://docs.flutter.dev/get-started/install/windows/mobile)
