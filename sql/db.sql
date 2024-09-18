-- Create `users` table
CREATE TABLE `users` (
    `userID` VARCHAR(256) PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL UNIQUE,
    `password` VARCHAR(120) NOT NULL,
    `firstname` VARCHAR(120) NOT NULL,
    `lastname` VARCHAR(120) NOT NULL,
    `dob` VARCHAR(120) NOT NULL
);

-- Add a test admin user with password admin
INSERT INTO `users` VALUES ("0","admin",MD5("admin"),"admin");

-- Create `tokens` table
CREATE TABLE `tokens` (
    `tokenID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `token` VARCHAR(256) NOT NULL UNIQUE,
    `dateIssue` VARCHAR(256) NOT NULL,
    CONSTRAINT `tokensFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

-- Create `podCategory` table
CREATE TABLE `podCategory` (
    `categoryID` VARCHAR(256) PRIMARY KEY UNIQUE,
    `categoryName` VARCHAR(256) NOT NULL
);

-- Create `podcasts` table
CREATE TABLE `podcasts` (
    `podID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `categoryID` VARCHAR(256) NOT NULL,
    `podName` VARCHAR(256) NOT NULL,
    `podUrl` VARCHAR(512) NOT NULL,
    `podDuration` INT NOT NULL DEFAULT 0,
    `updateDate` VARCHAR(256) NOT NULL,
    `interestID` VARCHAR(256) NOT NULL,
    CONSTRAINT `podcastsFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `podcastsFK2` FOREIGN KEY (`categoryID`) REFERENCES `podCategory`(`categoryID`),
    CONSTRAINT `podcastsFK3` FOREIGN KEY (`interestID`) REFERENCES `interests`(`interestID`)
);

CREATE TABLE `interests` (
    `interestID` VARCHAR(256) PRIMARY KEY,
    `interestName` VARCHAR(256) NOT NULL
);

INSERT INTO `interests` (`interestID`, `interestName`) VALUES
    ('0', 'No preference'),
    ('1', 'Art'),
    ('2', 'Music'),
    ('3', 'Comedy'),
    ('4', 'TV'),
    ('5', 'Government'),
    ('6', 'Sports'),
    ('7', 'Crypto'),
    ('8', 'Culture'),
    ('9', 'Society'),
    ('10', 'Business'),
    ('11', 'Health'),
    ('12', 'Education');

CREATE TABLE userinterest (
    transactionID VARCHAR(256) PRIMARY KEY,
    userID VARCHAR(256) NOT NULL,
    interestID VARCHAR(255) NOT NULL DEFAULT '0',
    CONSTRAINT `uiFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `uiFK2` FOREIGN KEY (`interestID`) REFERENCES `interests`(`interestID`)
);

-- Create `notes` table
CREATE TABLE `notes` (
    `noteID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `podID` VARCHAR(256) NOT NULL,
    `dateCreated` VARCHAR(256) NOT NULL,
    `content` TEXT NOT NULL,
    CONSTRAINT `notesFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `notesFK2` FOREIGN KEY (`podID`) REFERENCES `podcasts`(`podID`)
);

-- Create `library` table
CREATE TABLE `library` (
    `libraryID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) DEFAULT '0' NOT NULL,
    `libraryName` VARCHAR(256) NOT NULL,
    CONSTRAINT `libraryFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

-- Create `subscriptions` table
CREATE TABLE `subscriptions` (
    `subID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `libID` VARCHAR(256) NOT NULL,
    `dateOfSub` VARCHAR(256) NOT NULL,
    CONSTRAINT `subscrFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `subscrFK2` FOREIGN KEY (`libID`) REFERENCES `library`(`libraryID`)
);

-- Create `snippets` table-- Create `users` table
CREATE TABLE `users` (
    `userID` VARCHAR(256) PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL UNIQUE,
    `password` VARCHAR(120) NOT NULL,
    `role` VARCHAR(50) NOT NULL
);

-- Add a test admin user with password admin
INSERT INTO `users` VALUES ("0","admin",MD5("admin"),"admin");

-- Create `tokens` table
CREATE TABLE `tokens` (
    `tokenID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `token` VARCHAR(256) NOT NULL UNIQUE,
    `dateIssue` VARCHAR(256) NOT NULL,
    CONSTRAINT `tokensFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

-- Create `podCategory` table
CREATE TABLE `podCategory` (
    `categoryID` VARCHAR(256) PRIMARY KEY UNIQUE,
    `categoryName` VARCHAR(256) NOT NULL
);

-- Create `podcasts` table
CREATE TABLE `podcasts` (
    `podID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `categoryID` VARCHAR(256) NOT NULL,
    `podName` VARCHAR(256) NOT NULL,
    `podUrl` VARCHAR(512) NOT NULL,
    `podDuration` INT NOT NULL DEFAULT 0,
    `updateDate` VARCHAR(256) NOT NULL,
    CONSTRAINT `podcastsFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `podcastsFK2` FOREIGN KEY (`categoryID`) REFERENCES `podCategory`(`categoryID`)
);

-- Create `notes` table
CREATE TABLE `notes` (
    `noteID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `podID` VARCHAR(256) NOT NULL,
    `dateCreated` VARCHAR(256) NOT NULL,
    `content` TEXT NOT NULL,
    CONSTRAINT `notesFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `notesFK2` FOREIGN KEY (`podID`) REFERENCES `podcasts`(`podID`)
);

-- Create `library` table
CREATE TABLE `library` (
    `libraryID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) DEFAULT '0' NOT NULL,
    `libraryName` VARCHAR(256) NOT NULL,
    CONSTRAINT `libraryFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

-- Create `subscriptions` table
CREATE TABLE `subscriptions` (
    `subID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `libID` VARCHAR(256) NOT NULL,
    `dateOfSub` VARCHAR(256) NOT NULL,
    CONSTRAINT `subscrFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `subscrFK2` FOREIGN KEY (`libID`) REFERENCES `library`(`libraryID`)
);

-- Create `snippets` table
CREATE TABLE `snippets` (
    `snipID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `podID` VARCHAR(256) NOT NULL,
    `snippetContent` TEXT NOT NULL,
    `dateCreated` VARCHAR(256) NOT NULL,
    CONSTRAINT `snippetFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `snippetFK2` FOREIGN KEY (`podID`) REFERENCES `podcasts`(`podID`)
);

-- Create `podCategory` table
CREATE TABLE `podCategory` (
    `categoryID` VARCHAR(256) PRIMARY KEY,
    `categoryName` VARCHAR(256)
);

-- Create `resettokens` table
CREATE TABLE `resettokens` (
    `rtID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `token` VARCHAR(256) NOT NULL,
    `dateCreated` VARCHAR(256) NOT NULL,
    `used` INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT `resetTokenFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`)
);

CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_tokens_token ON tokens (token);
CREATE INDEX idx_notes_userID ON notes (userID);
CREATE INDEX idx_notes_podID ON notes (podID);
CREATE TABLE `snippets` (
    `snipID` VARCHAR(256) PRIMARY KEY,
    `userID` VARCHAR(256) NOT NULL,
    `podID` VARCHAR(256) NOT NULL,
    `snippetContent` TEXT NOT NULL,
    `dateCreated` VARCHAR(256) NOT NULL,
    CONSTRAINT `snippetFK1` FOREIGN KEY (`userID`) REFERENCES `users`(`userID`),
    CONSTRAINT `snippetFK2` FOREIGN KEY (`podID`) REFERENCES `podcasts`(`podID`)
);

-- Create `podCategory` table
CREATE TABLE `podCategory` (
    `categoryID` VARCHAR(256) PRIMARY KEY,
    `categoryName` VARCHAR(256)
);


CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_tokens_token ON tokens (token);
CREATE INDEX idx_notes_userID ON notes (userID);
CREATE INDEX idx_notes_podID ON notes (podID);
