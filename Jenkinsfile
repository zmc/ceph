pipeline {
  agent any
  parameters {
    string(name: "BRANCH", description: "The git branch (or tag) to build", defaultValue: "main")
    string(name: "DISTROS", description: "A list of distros to build for. Available options are: centos9, centos8, centos7, centos6, jammy, focal, bionic, xenial, trusty, precise, wheezy, jessie, and windows", defaultValue: "jammy focal bionic centos7 centos8 windows")
    string(name: "ARCHS", description: "A list of architectures to build for. Available options are: x86_64, and arm64", defaultValue: "x86_64 arm64")
    booleanParam(name: "THROWAWAY", description: "When true it will not POST binaries to chacra. Artifacts will not be around for long. Useful to test builds.", defaultValue: false)
    booleanParam(name: "FORCE", description: "If this is unchecked, then then nothing is built or pushed if they already exist in chacra. This is the default. If this is checked, then the binaries will be built and pushed to chacra even if they already exist in chacra.", defaultValue: false)
    string(name: "CEPH_BUILD_VIRTUALENV", description: "Base parent path for virtualenv locations, set to avoid issues with extremely long paths that are incompatible with tools like pip.", defaultValue: "/tmp/")
    choice(name: "FLAVOR", choices: ['default', 'crimson', 'jaeger'], description: "Type of Ceph build, choices are: crimson, jaeger, default.")
    string(name: "CI_CONTAINER", description: "Build container with development release of Ceph.  Note: this must be 'false' or 'true' so that it can execute a command or satisfy a string comparison", defaultValue: "true")
    string(name: "CONTAINER_REPO_HOSTNAME", description: "For CI_CONTAINER: Name of container repo server (i.e. 'quay.io')", defaultValue: "quay-quay-quay.apps.os.sepia.ceph.com")
    string(name: "CONTAINER_REPO_ORGANIZATION", description: "For CI_CONTAINER: Name of container repo organization (i.e. 'ceph-ci')", defaultValue: "ceph-ci")
    booleanParam(name: "DWZ", description: "Use dwz to make debuginfo packages smaller", defaultValue: true)
    booleanParam(name: "SCCACHE", description: "Use sccache", defaultValue: false)
  }
  stages {
    stage("setup") {
      steps {
        echo $params
        script {
          build job: "ceph-dev-new-setup", parameters: params
        }
      }
    }
    stage("build") {
      steps {
        script {
          copyArtifacts projectName: "ceph-dev-new-setup", filter: "dist/sha1", selector: downstream(upstreamProjectName: "${env.JOB_NAME}", upstreamBuildNumber: ${env.BUILD_ID})
          readProperties file: "${WORKSPACE}/dist/sha1"
          copyArtifacts projectName: "ceph-dev-new-setup", filter: "dist/branch", selector: downstream(upstreamProjectName: "${env.JOB_NAME}", upstreamBuildNumber: ${env.BUILD_ID})
          readProperties file: "${WORKSPACE}/dist/branch"
          buildName nameTemplate: "#${BUILD_NUMBER} ${BRANCH}, ${SHA1}, ${DISTROS}, ${FLAVOR}"
          build job: "ceph-dev-new-build", parameters: params
        }
      }
    }
  }
}
