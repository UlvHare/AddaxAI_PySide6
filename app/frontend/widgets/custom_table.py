# frontend/widgets/custom_table.py
from PySide6.QtWidgets import (
    QTableView, QAbstractItemView, QHeaderView, QStyledItemDelegate,
    QStyleOptionViewItem, QApplication
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QPainter

class CustomTableModel(QAbstractTableModel):
    """Custom table model for displaying and managing tabular data."""

    def __init__(self, data=None, headers=None, parent=None):
        """Initialize custom table model.

        Args:
            data: 2D list of data items
            headers: List of column headers
            parent: Parent widget
        """
        super().__init__(parent)
        self._data = data if data is not None else []
        self._headers = headers if headers is not None else []
        self._sort_column = 0
        self._sort_order = Qt.AscendingOrder

        # Default formatting for cells
        self._cell_formatting = {}  # (row, col): {"color": QColor, "bgcolor": QColor, "font": QFont}
        self._column_alignment = {}  # col: Qt.Alignment

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows."""
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns."""
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        """Return data for the given index and role."""
        if not index.isValid():
            return None

        row, col = index.row(), index.column()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if row < len(self._data) and col < len(self._data[row]):
                return str(self._data[row][col])
            return None

        elif role == Qt.TextAlignmentRole:
            return self._column_alignment.get(col, Qt.AlignLeft | Qt.AlignVCenter)

        elif role == Qt.FontRole:
            cell_format = self._cell_formatting.get((row, col), {})
            if "font" in cell_format:
                return cell_format["font"]
            return None

        elif role == Qt.ForegroundRole:
            cell_format = self._cell_formatting.get((row, col), {})
            if "color" in cell_format:
                return QBrush(cell_format["color"])
            return None

        elif role == Qt.BackgroundRole:
            cell_format = self._cell_formatting.get((row, col), {})
            if "bgcolor" in cell_format:
                return QBrush(cell_format["bgcolor"])
            return None

        return None

    def headerData(self, section, orientation, role):
        """Return header data for the given section, orientation and role."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal and section < len(self._headers):
                return self._headers[section]
            elif orientation == Qt.Vertical:
                return str(section + 1)

        return None

    def flags(self, index):
        """Return item flags for the given index."""
        if not index.isValid():
            return Qt.NoItemFlags

        # By default, items are enabled and selectable
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def sort(self, column, order):
        """Sort data by the specified column and order."""
        self.layoutAboutToBeChanged.emit()

        # Store sort parameters
        self._sort_column = column
        self._sort_order = order

        # Sort data
        if column < len(self._headers) and self._data:
            # Make sure column is valid for all rows
            valid_column = all(column < len(row) for row in self._data)

            if valid_column:
                # Sort using Python's built-in sort
                self._data.sort(
                    key=lambda row: (row[column] if column < len(row) else ""),
                    reverse=(order == Qt.DescendingOrder)
                )

        self.layoutChanged.emit()

    def setData(self, index, value, role=Qt.EditRole):
        """Set data for the given index and role."""
        if not index.isValid() or role != Qt.EditRole:
            return False

        row, col = index.row(), index.column()
        if row >= len(self._data) or col >= len(self._data[row]):
            return False

        # Update data
        self._data[row][col] = value
        self.dataChanged.emit(index, index)
        return True

    def setCellFormatting(self, row, col, color=None, bgcolor=None, font=None):
        """Set formatting for a specific cell.

        Args:
            row: Row index
            col: Column index
            color: Text color (QColor)
            bgcolor: Background color (QColor)
            font: Font (QFont)
        """
        formatting = {}
        if color is not None:
            formatting["color"] = color
        if bgcolor is not None:
            formatting["bgcolor"] = bgcolor
        if font is not None:
            formatting["font"] = font

        self._cell_formatting[(row, col)] = formatting

        # Notify views that the cell appearance has changed
        index = self.index(row, col)
        self.dataChanged.emit(index, index)

    def setColumnAlignment(self, column, alignment):
        """Set alignment for an entire column.

        Args:
            column: Column index
            alignment: Alignment flags (Qt.Alignment)
        """
        self._column_alignment[column] = alignment

        # Notify views that the column appearance has changed
        if self.rowCount() > 0:
            self.dataChanged.emit(
                self.index(0, column),
                self.index(self.rowCount() - 1, column)
            )

    def setData2D(self, data):
        """Set the entire data set.

        Args:
            data: 2D list of data items
        """
        self.beginResetModel()
        self._data = data
        self._cell_formatting = {}  # Reset formatting
        self.endResetModel()

    def setHeaders(self, headers):
        """Set column headers.

        Args:
            headers: List of column headers
        """
        self.beginResetModel()
        self._headers = headers
        self.endResetModel()

    def addRow(self, row_data):
        """Add a new row to the model.

        Args:
            row_data: List of data items for the new row
        """
        row_position = len(self._data)
        self.beginInsertRows(QModelIndex(), row_position, row_position)
        self._data.append(row_data)
        self.endInsertRows()

    def removeRow(self, row, parent=QModelIndex()):
        """Remove a row from the model.

        Args:
            row: Row index to remove
            parent: Parent index
        """
        if 0 <= row < len(self._data):
            self.beginRemoveRows(parent, row, row)
            del self._data[row]

            # Remove cell formatting for this row
            self._cell_formatting = {k: v for k, v in self._cell_formatting.items() if k[0] != row}
            # Adjust formatting keys for rows that got shifted up
            new_formatting = {}
            for (r, c), v in self._cell_formatting.items():
                if r > row:
                    new_formatting[(r-1, c)] = v
                else:
                    new_formatting[(r, c)] = v
            self._cell_formatting = new_formatting

            self.endRemoveRows()
            return True
        return False

    def clearData(self):
        """Clear all data from the model."""
        self.beginResetModel()
        self._data = []
        self._cell_formatting = {}
        self.endResetModel()


class CustomTable(QTableView):
    """Custom table view with enhanced functionality."""

    selectionChanged = Signal(list)  # Signal emitting selected row indices

    def __init__(self, parent=None):
        """Initialize custom table view.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Initialize the model and proxy model for sorting/filtering
        self._model = CustomTableModel()
        self._proxy_model = QSortFilterProxyModel()
        self._proxy_model.setSourceModel(self._model)
        self.setModel(self._proxy_model)

        # Configure appearance
        self.verticalHeader().setVisible(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)

        # Set default font
        font = QFont("sans")
        self.setFont(font)

        # Connect signals
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self, selected, deselected):
        """Handle selection changes in the table."""
        selected_rows = []
        for index in self.selectionModel().selectedRows():
            # Convert proxy index to source index
            source_index = self._proxy_model.mapToSource(index)
            selected_rows.append(source_index.row())

        self.selectionChanged.emit(selected_rows)

    def setData(self, data, headers=None):
        """Set data and optionally headers for the table.

        Args:
            data: 2D list of data items
            headers: List of column headers (optional)
        """
        if headers:
            self._model.setHeaders(headers)
        self._model.setData2D(data)

        # Adjust columns to content
        self.resizeColumnsToContents()

    def addRow(self, row_data):
        """Add a new row to the table.

        Args:
            row_data: List of data items for the new row
        """
        self._model.addRow(row_data)

    def removeSelectedRows(self):
        """Remove all selected rows from the table."""
        selected_rows = []
        for index in self.selectionModel().selectedRows():
            source_index = self._proxy_model.mapToSource(index)
            selected_rows.append(source_index.row())

        # Remove rows in descending order to avoid index shifting issues
        for row in sorted(selected_rows, reverse=True):
            self._model.removeRow(row)

    def clearData(self):
        """Clear all data from the table."""
        self._model.clearData()

    def setCellFormatting(self, row, col, color=None, bgcolor=None, font=None):
        """Set formatting for a specific cell.

        Args:
            row: Row index
            col: Column index
            color: Text color (QColor)
            bgcolor: Background color (QColor)
            font: Font (QFont)
        """
        self._model.setCellFormatting(row, col, color, bgcolor, font)

    def setColumnAlignment(self, column, alignment):
        """Set alignment for an entire column.

        Args:
            column: Column index
            alignment: Alignment flags (Qt.Alignment)
        """
        self._model.setColumnAlignment(column, alignment)

    def setFilterText(self, text):
        """Set filter text for the proxy model.

        Args:
            text: Filter text to match against all columns
        """
        self._proxy_model.setFilterRegExp(text)

    def setFilterColumn(self, column):
        """Set the column to filter on.

        Args:
            column: Column index to filter
        """
        self._proxy_model.setFilterKeyColumn(column)

    def getSelectedData(self):
        """Get data from selected rows.

        Returns:
            List of selected row data
        """
        selected_data = []
        for index in self.selectionModel().selectedRows():
            source_index = self._proxy_model.mapToSource(index)
            row = source_index.row()
            if row < len(self._model._data):
                selected_data.append(self._model._data[row])

        return selected_data

    def getAllData(self):
        """Get all data from the model.

        Returns:
            2D list of all data
        """
        return self._model._data.copy()
