use last_fm;


DROP TABLE IF EXISTS Artist_tag;
DROP TABLE IF EXISTS Track_tag;
DROP TABLE IF EXISTS Tags;
DROP TABLE IF EXISTS Listening_history;
DROP TABLE IF EXISTS Top_track;
DROP TABLE IF EXISTS Tracks;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Artists;

create table Users (
	user_id BIGINT NOT NULL AUTO_INCREMENT,
    user_name VARCHAR(50) NOT NULL,
    user_url VARCHAR(100) NOT NULL,
    primary key (user_id)
);

create table Artists (
	artist_id BIGINT NOT NULL,
    artist_name VARCHAR(50) NOT NULL,
    artist_url VARCHAR(100) NOT NULL,
    primary key (artist_id)
);

create table Tracks (
	track_id BIGINT NOT NULL,
    track_name VARCHAR(50) NOT NULL,
    track_url VARCHAR(100) NOT NULL,
    artist_id BIGINT NOT NULL,
    primary key (track_id),
    foreign key (artist_id) references Artists(artist_id)
);

create table Top_track (
	user_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    track_listening_count INTEGER NOT NULL DEFAULT 0,
    foreign key (user_id) references Users(user_id),
    foreign key (track_id) references Tracks(track_id)
);

create table Top_artist (
	user_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    artist_listening_count INTEGER NOT NULL DEFAULT 0,
    foreign key (user_id) references Users(user_id),
    foreign key (track_id) references Tracks(track_id)
);

create table Listening_history (
	user_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    listened_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    foreign key (user_id) references Users(user_id),
    foreign key (track_id) references Tracks(track_id)
);

create table Tags (
	tag_id BIGINT NOT NULL,
    tag_name VARCHAR(50) NOT NULL,
    tag_url VARCHAR(100) NOT NULL,
    primary key (tag_id)
);

create table Track_tag (
	tag_id BIGINT NOT NULL,
    track_id BIGINT NOT NULL,
    foreign key (tag_id) references Tags(tag_id),
    foreign key (track_id) references Tracks(track_id)
);

create table Artist_tag (
	tag_id BIGINT NOT NULL,
    artist_id BIGINT NOT NULL,
    foreign key (tag_id) references Tags(tag_id),
    foreign key (artist_id) references Artists(artist_id)
);