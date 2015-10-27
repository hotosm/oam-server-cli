# OpenAerialMap Command Line client

This is a CLI that interacts with the OAM server API.

### Installing

Clone this repository, run `python setup.py install`

### Commands

#### jobs

```
oam jobs
```

Prints information about every job run.

#### info

```
oam info 345ef
```

Prints information about a specific job. You only need to type in as much of the Job ID as makes it distinct from other jobs.

#### tile

```
oam tile s3://bucket/image.tif s3://bucket/image2.tif
```

or

```
oam tile -f images.txt
```

where `images.txt` would look like

```
s3://bucket/image.tif
s3://bucket/image2.tif
s3://bucket/image3.tif
```

This will kick off a tiling job and print out the job ID that you can use to track it's status.
