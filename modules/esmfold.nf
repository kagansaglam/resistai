process RUN_ESMFOLD {
    publishDir "${params.outdir}/structures", mode: 'copy'

    input:
    tuple val(uniprot_id), path(fasta)

    output:
    tuple val(uniprot_id), path("${uniprot_id}.pdb"), emit: pdb

    script:
    """
    python3 ${projectDir}/scripts/run_esmfold.py ${uniprot_id} ${fasta}
    """
}
