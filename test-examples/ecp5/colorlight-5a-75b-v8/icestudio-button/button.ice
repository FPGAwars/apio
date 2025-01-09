{
  "version": "1.2",
  "package": {
    "name": "",
    "version": "",
    "description": "",
    "author": "",
    "image": ""
  },
  "design": {
    "board": "colorlight-5a-75b-v8",
    "graph": {
      "blocks": [
        {
          "id": "0712d438-b46d-411e-87bf-e4379d7fae23",
          "type": "basic.output",
          "data": {
            "name": "LED",
            "virtual": false,
            "pins": [
              {
                "index": "0",
                "name": "LED",
                "value": "T6"
              }
            ]
          },
          "position": {
            "x": 512,
            "y": 216
          }
        },
        {
          "id": "650576bb-aac4-487c-abad-ad2249663e7e",
          "type": "basic.input",
          "data": {
            "name": "MY_INPUT",
            "virtual": false,
            "pins": [
              {
                "index": "0",
                "name": "Button",
                "value": "R7"
              }
            ],
            "clock": false
          },
          "position": {
            "x": 304,
            "y": 216
          }
        }
      ],
      "wires": [
        {
          "source": {
            "block": "650576bb-aac4-487c-abad-ad2249663e7e",
            "port": "out"
          },
          "target": {
            "block": "0712d438-b46d-411e-87bf-e4379d7fae23",
            "port": "in"
          }
        }
      ]
    }
  },
  "dependencies": {}
}