# EZ Maps
> Generate Beautiful Maps 🗺

## Contents
- [Installation](#install)
- [Usage](#use)
- [Examples](#exam)
- [Troubleshooting](#tb)
- [Contributing](#cb)
- [Author](#author)
- [License](#ls)

<a name="install"></a>
## Installation
* Make sure you have Python installed (Python 3.2+)
* You can install using the command `pip3 install ezmaps`

<a name="use"></a>
## Usage
*  This is a CLI app so you can run it using `ezmaps` in your command line
* ezmaps takes a few arguments

			* -c , --config  Path to your config file
			* -s , --save    If you save the state of this run
			* -l , --load	 Load an old state (pickle file) to avoid makes calls to the API

* The config file is in the `json` format and has the following information
````
{
	"details":{
		"place": "Sydney"
		"level":7,
		"background": [0,0,0],
	    "color":[255,255,255],
	    "size":[2500,1800],
		"detail":6
	},
	"markers": [{
		"locations": ["police"],
		"icon": "police.png",
		"size": 30
	}]
}
````

|key|type|description|
|----|----|----|
|`[details],[place]`|`string`| The name of the place you want to generate the map for
|`[details][level]`|`integer`|Administrative level for the place you can find the level for your place [here](https://wiki.openstreetmap.org/wiki/Tag:boundary%3Dadministrative#10_admin_level_values_for_specific_countries)
|`[details][background]`|`list or integer`|RGB value of the color you want or `-1`-Transparent
|`[details][color]`|`list`|RGB values for the color you want the map to be drawn in
|`[details][size]`|`list or integer`|`width and height` of the output image (The actual image will be resized to this value). If just an `integer` is provided it returns the natural scale of the map with the integer as the max height or width value allowed
|`[details][detail]`|`list`|How many level of roads do you want in your image higher the number the lower the level of roads fetched
|`[markers]`|`list`|A list of markers you want marked on your image
|`[markers][locations]`|`list or string`|A list of longitude or latitude for custom markers or a string specifying a type of important location
|`[markers][icon]`|`string`|Path to the icon you want the mark the marker with will search in folder `icon` in the location where the config file is located
|`[markers][size]`|`integer`|Size of the icon in the final image in `pixles`

<a name="exam"></a>
## Examples
All `json` files for the examples can be found in `tests` folder

### Sydney
Marking all cafes in Sydney
![sydney](https://user-images.githubusercontent.com/10531093/73243416-74afc980-41cd-11ea-8a28-d0aace2914c1.png)


### California
Custom Marking `Los Angeles` and `San Francisco` in California

![california](https://user-images.githubusercontent.com/10531093/73245150-9448f100-41d1-11ea-9da7-dc6b30258cf5.png)

### Argentina
![argentina](https://user-images.githubusercontent.com/10531093/73247934-fc9ad100-41d7-11ea-8600-c18e266175cb.png)


### Shibuya
Marking all `hospitals` in Shibuya

![shibuya](https://user-images.githubusercontent.com/10531093/73247776-a7f75600-41d7-11ea-8bda-24088e4671bd.png)


<a name="tb"></a>
## Troubleshooting

- All this data is obtained from [Overpass](https://wiki.openstreetmap.org/wiki/Overpass_API) which is rate-limited so to avoid getting stuck in the rate-limit try saving and loading states as much as possible
-  If you find any bug or error please create an Issue on this repository


<a name="cb"></a>
## Contributing

All Contributions welcome
Please submit all pull requests the against master branch.

<a name="auth"></a>
## Author

[c00kie17](https://github.com/c00kie17)

<a name="ls"></a>
## License

[**MIT**](http://opensource.org/licenses/MIT)


