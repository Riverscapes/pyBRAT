module.exports = function(grunt) {
  grunt.initConfig({

    // Grunt-sass 
    // sass (libsass) config
    sass: {
        options: {
            sourceMap: true,
            relativeAssets: false,
            outputStyle: 'compressed',
            sassDir: 'scss',
            cssDir: '../assets/css',
            includePaths: [
              'node_modules/foundation-sites/scss',
              'node_modules/font-awesome/scss',
            ]
        },
        build: {
            files: [{
                expand: true,
                cwd: 'scss/',
                src: ['**/*.scss'],
                dest: '../assets/css',
                ext: '.css'
            }]
        }
    },

  });

  // Define the modules we need for these tasks:
  grunt.loadNpmTasks('grunt-sass');

  // Here are our tasks 
  grunt.registerTask('default', [ 'build' ]);
  grunt.registerTask('build', [ 'sass' ]);
  grunt.registerTask('dev', [ 'watch' ]);

};