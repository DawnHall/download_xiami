CREATE TABLE IF NOT EXISTS SONG (
	SONG_ID integer primary key not null,
	SONG_NAME text not null,
	SONG_URL text,
	SONG_ALBUM text,
	SONG_ALBUM_LINK text,
	SINGER text,
	SINGER_LINK text,	
	WEB text default "虾米"
);

CREATE TABLE IF NOT EXISTS USER (
	USER_ID integer primary key not null,
	USER_NAME text,
	SONG_ALL integer
);

CREATE TABLE IF NOT EXISTS SEARCH (
	SONG_ID not null REFERENCES SONG(SONG_ID),
	USER_ID not null REFERENCES USER(USER_ID),
	PRIMARY KEY (SONG_ID, USER_ID)
);