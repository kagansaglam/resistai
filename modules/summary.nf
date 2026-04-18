process SUMMARY_REPORT {
    publishDir "${params.outdir}", mode: 'copy'

    input:
    path(json_files)

    output:
    path("summary_report.csv"), emit: report

    script:
    """
    python3 ${projectDir}/scripts/summary_report.py ${json_files}
    """
}
