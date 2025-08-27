const path = require('path');
const postcssPresetEnv = require('postcss-preset-env');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  entry: {
    draftail: './src/wagtail_ai/static_src/draftail/main.tsx',
    image_description: './src/wagtail_ai/static_src/image_description/main.tsx',
    field_panel: './src/wagtail_ai/static_src/field_panel/main.ts',
  },
  plugins: [new MiniCssExtractPlugin()],
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          { loader: 'css-loader', options: { importLoaders: 1 } },
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [postcssPresetEnv()],
              },
            },
          },
        ],
      },
      {
        test: /\.svg$/,
        type: 'asset/source',
      },
      {
        test: /\.(png|jpg|gif)$/,
        use: ['file-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  externals: {
    /* These are provided by Wagtail */
    'react': 'React',
    'react-dom': 'ReactDOM',
    'gettext': 'gettext',
    'draftail': 'Draftail',
    'draft-js': 'DraftJS',
    '@hotwired/stimulus': 'StimulusModule',
  },
  output: {
    path: path.resolve(__dirname, 'src/wagtail_ai/static/wagtail_ai'),
    filename: '[name].js',
  },
};
