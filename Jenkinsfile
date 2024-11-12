pipeline {
  agent any
  stages {
    stage("setup") {
      steps {
        echo $params
        script {
          build(
            job: "ceph-dev-new-setup",
            parameters: [
              string(name: "BRANCH", value: env.BRANCH),
              string(name: "DISTROS", value: env.DISTROS),
              string(name: "ARCHS", value: env.ARCHS),
              booleanParam(name: "THROWAWAY", value: env.THROWAWAY),
              booleanParam(name: "FORCE", value: env.FORCE),
              string(name: "FLAVOR", value: env.FLAVOR),
              string(name: "CI_CONTAINER", value: env.CI_CONTAINER),
              booleanParam(name: "DWZ", value: env.DWZ),
              booleanParam(name: "SCCACHE", value: env.SCCACHE),
            ]
          )
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
          build(
            job: "ceph-dev-new-build",
            parameters: [
              string(name: "BRANCH", value: env.BRANCH),
              string(name: "DISTROS", value: env.DISTROS),
              string(name: "ARCHS", value: env.ARCHS),
              booleanParam(name: "THROWAWAY", value: env.THROWAWAY),
              booleanParam(name: "FORCE", value: env.FORCE),
              string(name: "FLAVOR", value: env.FLAVOR),
              string(name: "CI_CONTAINER", value: env.CI_CONTAINER),
              booleanParam(name: "DWZ", value: env.DWZ),
              booleanParam(name: "SCCACHE", value: env.SCCACHE),
            ]
          )
        }
      }
    }
  }
}
