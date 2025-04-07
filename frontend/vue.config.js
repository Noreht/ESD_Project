// vue.config.js
module.exports = {
  devServer: {
    proxy: {
      "/categorisation": {
        target: "http://localhost:3000", // gateway.js
        changeOrigin: true,
      },
    },
  },
};
