CREATE TABLE shp.ruler3d (
	id serial NOT NULL,
	box_id varchar NOT NULL,
	length numeric NULL,
	width numeric NULL,
	height numeric NULL,
	ins_ts timestamp without time zone DEFAULT now () NOT NULL,
	CONSTRAINT ruler3d_pk PRIMARY KEY (id)
);

