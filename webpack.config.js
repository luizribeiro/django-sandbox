var baseDir = __dirname + "/backend/static/js";

module.exports = {
  context: baseDir + "/src",
  entry: {
    main: "./main.js"
  },
  output: {
    path: baseDir + "/dist",
    filename: "[name].js"
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        loader: "babel-loader",
        query: {
          presets: ["es2015", "react", "flow"]
        }
      }
    ]
  }
};
