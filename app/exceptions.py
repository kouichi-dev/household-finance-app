

class EmailAlreadyExistsError(Exception):
    """email が既に使われているとき crud が投げる業務例外。
    HTTP に依存しない。service が HTTPException(409) に翻訳する。"""
    pass

class CategoryAlreadyExistsError(Exception):
    """同名カテゴリが既に存在するとき crud が投げる業務例外。
    HTTP に依存しない。service が HTTPException(409) に翻訳する。"""
    pass

class TokenAlreadyExistsError(Exception):
    """refresh_token が重複したとき crud　が投げる業務例外。"""
    pass