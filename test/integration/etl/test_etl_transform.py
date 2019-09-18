"""Tests for etl copy functions.  This includes application of transforms.
These are run against PostgreSQL."""
# pylint: disable=unused-argument, missing-docstring

from etlhelper import iter_rows, copy_rows


def test_copy_rows_happy_path(pgtestdb_conn, pgtestdb_test_tables,
                              pgtestdb_insert_sql, test_table_data):
    # Arrange and act
    select_sql = "SELECT * FROM src"
    insert_sql = pgtestdb_insert_sql.replace('src', 'dest')
    copy_rows(select_sql, pgtestdb_conn, insert_sql, pgtestdb_conn)

    # Assert
    sql = "SELECT * FROM dest"
    result = iter_rows(sql, pgtestdb_conn)
    assert list(result) == test_table_data


def test_copy_rows_transform(pgtestdb_conn, pgtestdb_test_tables):
    # Arrange
    select_sql = "SELECT * FROM src"
    insert_sql = "INSERT INTO dest (id) VALUES (%s)"

    def my_transform(rows):
        # Simple transform function that changes size and number of rows
        return [(row.id,) for row in rows if row.id > 1]

    expected = [(2, None, None, None, None, None),
                (3, None, None, None, None, None)]

    # Act
    copy_rows(select_sql, pgtestdb_conn, insert_sql, pgtestdb_conn,
              transform=my_transform)

    # Assert
    sql = "SELECT * FROM dest"
    result = iter_rows(sql, pgtestdb_conn)
    assert list(result) == expected
