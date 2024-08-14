-- Create `users` table
CREATE TABLE `users` (
    `userID` VARCHAR(256) PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL UNIQUE,
    `password` VARCHAR(120) NOT NULL,
    `role` VARCHAR(50) NOT NULL
);

-- Create a default admin user
INSERT INTO users VALUES ("0","admin",MD5("admin"),"admin");

-- Create `tokens` table
CREATE TABLE `tokens` (
    `tokenID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `token` VARCHAR(256) NOT NULL UNIQUE,
    `dateIssue` VARCHAR(256) NOT NULL,
    FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

-- Create `notes` table
CREATE TABLE `notes` (
    `noteID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `podID` VARCHAR(256) NOT NULL,
    `dateCreated` VARCHAR(256) NOT NULL,
    `content` TEXT NOT NULL,
    FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    FOREIGN KEY (`podID`) REFERENCES `podcasts`(`podID`)
);

-- Create `library` table
CREATE TABLE `library` (
    `libraryID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) DEFAULT '0',
    `libraryName` VARCHAR(256) NOT NULL,
    FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

-- Create `subscriptions` table
CREATE TABLE `subscriptions` (
    `subID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `libID` VARCHAR(256) NOT NULL,
    `dateOfSub` VARCHAR(256) NOT NULL,
    FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    FOREIGN KEY (`libID`) REFERENCES `library`(`libraryID`)
);

-- Create `podcasts` table
CREATE TABLE `podcasts` (
    `podID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `podName` VARCHAR(256) NOT NULL,
    `podUrl` VARCHAR(512) NOT NULL,
    FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

-- Create `snippets` table
CREATE TABLE `snippets` (
    `snipID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `podID` VARCHAR(256) NOT NULL,
    `snippetContent` TEXT NOT NULL,
    `dateCreated` VARCHAR(256) NOT NULL,
    FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    FOREIGN KEY (`podID`) REFERENCES `podcasts`(`podID`)
);
