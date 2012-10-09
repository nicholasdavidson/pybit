INSERT INTO arch (name) VALUES
	('armel'),
	('armel-cross'),
	('i386');

INSERT INTO distribution(name) VALUES
	('Debian');

INSERT INTO suite(name) VALUES
	('chickpea'),
	('development');

INSERT INTO format(name) VALUES
	('deb');

INSERT INTO package(name, version) VALUES
	('logicalmodel','0.4.42'),
	('logicalmodel','0.4.39chickpea4');

INSERT INTO packageinstance(package_id, arch_id, suite_id, dist_id, format_id) VALUES ( 
	(SELECT id FROM package WHERE name='logicalmodel' AND version='0.4.39chickpea4'),
	(SELECT id FROM arch WHERE name='armel'),
	(SELECT id FROM suite WHERE name='chickpea'),
	(SELECT id FROM distribution WHERE name='Debian'),
	(SELECT id FROM format WHERE name='deb'));

 INSERT INTO packageinstance(package_id, arch_id, suite_id, dist_id, format_id) VALUES (
	(SELECT id FROM package WHERE name='logicalmodel' AND version='0.4.39chickpea4'),
	(SELECT id FROM arch WHERE name='i386'),
 	(SELECT id FROM suite WHERE name='chickpea'),
	(SELECT id FROM distribution WHERE name='Debian'),
	(SELECT id FROM format WHERE name='deb'));

INSERT INTO packageinstance(package_id, arch_id, suite_id, dist_id, format_id) VALUES (
	(SELECT id FROM package WHERE name='logicalmodel' AND version='0.4.42'),
	(SELECT id FROM arch WHERE name='armel'),
	(SELECT id FROM suite WHERE name='development'),
	(SELECT id FROM distribution WHERE name='Debian'),
	(SELECT id FROM format WHERE name='deb'));

INSERT INTO packageinstance(package_id, arch_id, suite_id, dist_id, format_id) VALUES (
	(SELECT id FROM package WHERE name='logicalmodel' AND version='0.4.42'),
	(SELECT id FROM arch WHERE name='i386'),
	(SELECT id FROM suite WHERE name='development'),
	(SELECT id FROM distribution WHERE name='Debian'),
	(SELECT id FROM format WHERE name='deb'));

INSERT INTO buildclients(name) VALUES 
	('arm01'),
	('arm02'),
	('buildbox');
INSERT INTO status(name) VALUES
	('Waiting'),
	('Blocked'),
	('Building'),
	('Failed'),
	('Uploaded'),
	('Done');
