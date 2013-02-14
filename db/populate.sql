INSERT INTO arch (name) VALUES
	('armel'),
	('i386');

INSERT INTO distribution(name) VALUES
	('Debian');

INSERT INTO suite(name) VALUES
	('chickpea'),
	('development'),
	('illgill');

INSERT INTO format(name) VALUES
	('deb');

INSERT INTO suitearches(suite_id, arch_id, master_weight) VALUES (
	(SELECT id FROM suite WHERE name='development'),
	(SELECT id FROM arch WHERE name='armel'),
	0
);

INSERT INTO suitearches(suite_id, arch_id,master_weight) VALUES (
	(SELECT id FROM suite WHERE name='development'),
	(SELECT id FROM arch WHERE name='i386'),
	1
);

INSERT INTO suitearches(suite_id, arch_id,master_weight) VALUES (
	(SELECT id FROM suite WHERE name='chickpea'),
	(SELECT id FROM arch WHERE name='armel'),
	0
);

INSERT INTO suitearches(suite_id, arch_id,master_weight) VALUES (
	(SELECT id FROM suite WHERE name='chickpea'),
	(SELECT id FROM arch WHERE name='i386'),
	1
);

INSERT INTO suitearches(suite_id, arch_id,master_weight) VALUES (
	(SELECT id FROM suite WHERE name='illgill'),
	(SELECT id FROM arch WHERE name='armel'),
	0
);

INSERT INTO suitearches(suite_id, arch_id,master_weight) VALUES (
	(SELECT id FROM suite WHERE name='illgill'),
	(SELECT id FROM arch WHERE name='i386'),
	1
);

INSERT INTO buildenv(name) VALUES ('squeeze');
INSERT INTO buildenv(name) VALUES ('wheezy');

INSERT INTO buildclients(name) VALUES 
	('build_client_pyarm01'),
	('build_client_arm02'),
	('build_client_buildbox');

INSERT INTO status(name) VALUES
	('Waiting'),
	('Blocked'),
	('Cancelled'),
	('Building'),
	('Failed'),
	('Uploaded'),
	('Done');
