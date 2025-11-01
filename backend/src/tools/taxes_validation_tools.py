from langchain.tools import tool

# Tolerância de casas decimais para erros em cálculo de impostos
TOLERANCE = 0.01


def create_validation_tools(session_id: str):
    """Função para criação das ferramentas com injeção de dependências.

    Args:
        session_id (str): Identificador da sessão atual.

    Returns:
        list (BaseTool): Lista de ferramentas do agente.
    """

    # TODO: Requer certificado digital ou APIs externas
    async def check_nfe_exists(access_key: str):
        """Search if nfe exists with the provided access key in the SEFAZ database."""
        return NotImplemented

    @tool('validate_document_header')
    async def validate_document_header(access_key: str, issuer_cnpj: str):
        """Check if the provided fields are valid fields for invoice documents (nfe) in Brazil.

        Args:
            access_key (str): Is the nfe 44 digits identifier key.
            issuer_cnpj (str): Is the issuer company cnpj with 14 digits.
        """

        issuer_cnpj = issuer_cnpj.replace('.', '').replace('-', '')

        # Validação da chave de acesso
        access_key_size = len(access_key)
        is_valid_access_key = access_key_size == 44
        size_message = 'lower' if access_key_size < 44 else 'greater'

        if not is_valid_access_key:
            return {
                'error': f'Invalid access key, value is {size_message} than 44 digits. Counted {access_key_size} digits!'
            }

        try:
            int(access_key)
        except ValueError:
            return {'error': 'Invalid access key, non-numeric digit found!'}

        # validação do cnpj do emitente
        cnpj_size = len(issuer_cnpj)
        is_valid_cnpj = cnpj_size == 14

        if not is_valid_cnpj:
            return {
                'error': f'Invalid cnpj received with more than 14 digits. Counted {cnpj_size} digits!'
            }

        return {'success', 'The fields received have been validated successfully!'}

    @tool('validate_icms')
    async def validate_icms_compliance(
        item_id: int,
        cst_icms: str,
        v_prod: float,
        v_bc_icms: float,
        p_icms: float,
        v_icms: float,
        is_simples_nacional: bool = False,
    ):
        """
        Checks if the highlighted ICMS value (v_icms) complies with the CST, Tax Base, and Rate.
        Must be called for each item (product) in the fiscal invoice.

        Args:
            item_id: ID or sequential number of the item for reference.
            cst_icms: ICMS Tax Situation Code (CST) or CSOSN (e.g., "00", "41", "101").
            v_prod: Gross product value (vProd).
            v_bc_icms: ICMS Tax Base Value (vBCICMS).
            p_icms: ICMS Rate Percentage (pICMS), in decimal (e.g., 0.18 for 18%).
            v_icms: ICMS value highlighted on the invoice (vICMS).
            is_simples_nacional: Flag indicating if the issuer is under the Simples Nacional regime.
        """
        result = {
            'item_id': item_id,
            'status_icms': 'VALIDO',
            'error_type': None,
            'expected_v_icms': 0.0,
        }

        # Rule 1: Validation for Simples Nacional (CSOSN)
        if is_simples_nacional and cst_icms not in ['101', '201', '900']:
            # For most CSOSN codes, highlighting is prohibited (vICMS must be zero)
            if v_icms > TOLERANCE:
                result['status_icms'] = 'SN_TAX_HIGHLIGHT_ERROR'
                result['error_type'] = 'Undue ICMS highlight for the tax regime.'
                return result
            result['status_icms'] = 'EXEMPT_SN_COMPLIANT'
            return result

        # Rule 2: Fully Taxed ICMS (CST 00)
        if cst_icms == '00':
            expected_v_icms = round(v_bc_icms * p_icms, 2)
            result['expected_v_icms'] = expected_v_icms
            if abs(v_icms - expected_v_icms) > TOLERANCE:
                result['status_icms'] = 'CALCULATION_INCONSISTENCY'
                result['error_type'] = (
                    'Calculated ICMS diverges from the highlighted value.'
                )

        # Rule 3: Exempt or Non-Taxable ICMS (CST 40, 41, 50, 51)
        elif cst_icms in ['40', '41', '50', '51']:
            if v_icms > TOLERANCE or v_bc_icms > TOLERANCE:
                result['status_icms'] = 'UNDUE_TAX_ERROR'
                result['error_type'] = (
                    'ICMS highlight in an exempt/non-taxable operation.'
                )

        # Rule 4: ICMS previously charged via ST (CST 60)
        elif cst_icms == '60':
            if v_icms > TOLERANCE:
                result['status_icms'] = 'ICMS_ST_ERROR'
                result['error_type'] = (
                    'Undue ICMS highlight (previously charged via ST).'
                )

        # Rule 5: Other CSTs (10, 20, 30, 70, 90) - Require specific logic for reduced base or ST
        # For the current scope, we just flag attention if the calculation is not 0.00
        else:
            # If it's a CST that implies calculation (10, 70, 90), we validate the basic base/rate
            if v_icms > TOLERANCE:
                expected_v_icms = round(v_bc_icms * p_icms, 2)
                result['expected_v_icms'] = expected_v_icms
                if abs(v_icms - expected_v_icms) > TOLERANCE:
                    result['status_icms'] = 'ATTENTION_CALCULATION'
                    result['error_type'] = (
                        f'ICMS calculation ({cst_icms}) requires verification of Reduced Base/ST.'
                    )

        return result

    ### 3. Tool for Federal Taxes Validation (PIS, COFINS, and IPI)

    @tool('validate_federal_taxes')
    def validate_federal_taxes(
        item_id: int,
        is_simples_nacional: bool,
        cst_ipi: str,
        v_bc_ipi: float,
        p_ipi: float,
        v_ipi: float,
        cst_pis: str,
        v_bc_pis: float,
        p_pis: float,
        v_pis: float,
        cst_cofins: str,
        v_bc_cofins: float,
        p_cofins: float,
        v_cofins: float,
    ):
        """
        Checks the compliance of IPI, PIS, and COFINS based on the CST/NCM and the issuer's tax regime.

        Args:
            item_id: ID or sequential number of the item.
            is_simples_nacional: Flag indicating if the issuer is under the Simples Nacional regime.
            ... other calculation and highlighted value fields for IPI, PIS, and COFINS.
        """

        inconsistencies = []

        # Rule 1: General Validation - Simples Nacional (Prohibition of highlight)
        if is_simples_nacional:
            if v_ipi > TOLERANCE:
                inconsistencies.append(
                    'IPI_ERROR: Undue IPI highlight for Simples Nacional.'
                )
            if v_pis > TOLERANCE:
                inconsistencies.append(
                    'PIS_ERROR: Undue PIS highlight for Simples Nacional.'
                )
            if v_cofins > TOLERANCE:
                inconsistencies.append(
                    'COFINS_ERROR: Undue COFINS highlight for Simples Nacional.'
                )

            # If errors were found in SN, verification for this item ends
            if inconsistencies:
                return {
                    'item_id': item_id,
                    'status_federal': 'SN_NON_COMPLIANT',
                    'inconsistencies': inconsistencies,
                }

        # Rule 2: IPI Calculation Validation (CST 50 - Taxed)
        if cst_ipi == '50':
            expected_v_ipi = round(v_bc_ipi * p_ipi, 2)
            if abs(v_ipi - expected_v_ipi) > TOLERANCE:
                inconsistencies.append(
                    f'IPI_INCONSISTENCY: IPI calculation (R$ {v_ipi}) diverges from expected (R$ {expected_v_ipi}).'
                )

        # Rule 3: PIS Calculation Validation (CST 01 - Taxed Basic Rate)
        if cst_pis == '01':
            expected_v_pis = round(v_bc_pis * p_pis, 2)
            if abs(v_pis - expected_v_pis) > TOLERANCE:
                inconsistencies.append(
                    f'PIS_INCONSISTENCY: PIS calculation (R$ {v_pis}) diverges from expected (R$ {expected_v_pis}).'
                )

        # Rule 4: COFINS Calculation Validation (CST 01 - Taxed Basic Rate)
        if cst_cofins == '01':
            expected_v_cofins = round(v_bc_cofins * p_cofins, 2)
            if abs(v_cofins - expected_v_cofins) > TOLERANCE:
                inconsistencies.append(
                    f'COFINS_INCONSISTENCY: COFINS calculation (R$ {v_cofins}) diverges from expected (R$ {expected_v_cofins}).'
                )

        # Rule 5: Exemption Validation (CST 04 - PIS/COFINS Exempt)
        if cst_pis == '04' and v_pis > TOLERANCE:
            inconsistencies.append(
                'PIS_ERROR: PIS highlight in an Exempt operation (CST 04).'
            )
        if cst_cofins == '04' and v_cofins > TOLERANCE:
            inconsistencies.append(
                'COFINS_ERROR: COFINS highlight in an Exempt operation (CST 04).'
            )

        return {
            'status_federal': 'COMPLIANT'
            if not inconsistencies
            else 'NON COMPLIANCE DETECTED',
            'inconsistencies': inconsistencies,
        }

    ### 4. Tool for Total Note Value Validation (Closing Level)

    @tool('validate_total_note_value')
    def validate_total_note_value(
        v_nf_declarado: float,
        total_v_prod: float,
        total_v_ipi: float,
        total_v_icms_st: float,
        total_v_outras_despesas: float,
        total_v_descontos: float,
    ):
        """
        Checks if the Total Note Value (vNF) corresponds to the sum of all items and highlighted taxes,
        using consolidated totals.

        Args:
            v_nf_declarado: Declared Total Note Value (vNF) from the XML.
            total_v_prod: Sum of all vProd from items.
            total_v_ipi: Sum of all vIPI from items.
            total_v_icms_st: Sum of all vICMSST from items.
            total_v_outras_despesas: Sum of other accessory expenses.
            total_v_descontos: Sum of discounts.
        """

        # Standard formula for vNF calculation (Simplified)
        v_nf_calculated = (
            total_v_prod
            + total_v_ipi
            + total_v_icms_st
            + total_v_outras_despesas
            - total_v_descontos
        )

        # Rounding to prevent floating point errors, using the defined tolerance
        v_nf_calculated = round(v_nf_calculated, 2)

        is_mismatch = abs(v_nf_declarado - v_nf_calculated) > TOLERANCE

        if not is_mismatch:
            return {'status': 'COMPLIANT'}
        else:
            {
                'status': 'TOTAL MISMATCH DETECTED',
                'v_nf_calculated': v_nf_calculated,
                'v_nf_declared': v_nf_declarado,
                'is_mismatch': is_mismatch,
                'details': f'Difference of R$ {abs(v_nf_declarado - v_nf_calculated):.2f}',
            }

    return [
        validate_document_header,
        validate_federal_taxes,
        validate_icms_compliance,
        validate_total_note_value,
    ]
