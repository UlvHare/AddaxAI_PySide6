# frontend/widgets/species_selector.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QScrollArea, QLineEdit, QGroupBox, QSizePolicy, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

class SpeciesSelector(QWidget):
    """Widget for selecting species/categories from a list."""

    selectionChanged = Signal(list)  # Signal emitting selected species

    def __init__(self, parent=None, multi_select=True):
        """Initialize the species selector widget.

        Args:
            parent: Parent widget
            multi_select: Whether multiple species can be selected
        """
        super().__init__(parent)

        self.multi_select = multi_select
        self.species_list = []
        self.checkboxes = {}

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        # Header with title and buttons
        header_layout = QHBoxLayout()
        self.title_label = QLabel("Species Selection")
        self.title_label.setFont(QFont("sans", 10, QFont.Bold))

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all)
        self.select_all_button.setFixedWidth(80)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_selection)
        self.clear_button.setFixedWidth(80)

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.select_all_button)
        header_layout.addWidget(self.clear_button)

        main_layout.addLayout(header_layout)

        # Filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter species...")
        self.filter_input.textChanged.connect(self.filter_species)
        main_layout.addWidget(self.filter_input)

        # Scroll area for checkboxes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(2)
        self.scroll_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # Hide these buttons if not multiselect
        if not self.multi_select:
            self.select_all_button.setVisible(False)
            self.clear_button.setVisible(False)

            # Add a combo box instead for single selection
            self.species_combo = QComboBox()
            self.species_combo.currentIndexChanged.connect(self.on_combo_changed)
            main_layout.insertWidget(1, self.species_combo)
            self.filter_input.setVisible(False)
            self.scroll_area.setVisible(False)

    def add_species(self, species_list):
        """Add species to the selector.

        Args:
            species_list: List of species names
        """
        self.species_list = sorted(species_list) if species_list else []

        # Clear existing checkboxes and combo items
        self.clear_ui()

        if self.multi_select:
            # Create checkboxes for each species
            for species in self.species_list:
                checkbox = QCheckBox(species)
                checkbox.stateChanged.connect(self.on_selection_changed)
                self.checkboxes[species] = checkbox
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, checkbox)
        else:
            # Add items to combo box
            self.species_combo.clear()
            self.species_combo.addItem("-- Select Species --")
            self.species_combo.addItems(self.species_list)

    def clear_ui(self):
        """Clear all UI elements."""
        if self.multi_select:
            # Remove all checkboxes
            for checkbox in self.checkboxes.values():
                self.scroll_layout.removeWidget(checkbox)
                checkbox.deleteLater()
            self.checkboxes = {}
        else:
            # Clear combo box
            self.species_combo.clear()

    def get_selected_species(self):
        """Get the currently selected species.

        Returns:
            List of selected species names
        """
        if self.multi_select:
            return [species for species, checkbox in self.checkboxes.items()
                   if checkbox.isVisible() and checkbox.isChecked()]
        else:
            index = self.species_combo.currentIndex()
            if index > 0:  # Skip the first item (placeholder)
                return [self.species_combo.currentText()]
            return []

    def select_all(self):
        """Select all visible species."""
        if not self.multi_select:
            return

        for checkbox in self.checkboxes.values():
            if checkbox.isVisible():
                checkbox.setChecked(True)

    def clear_selection(self):
        """Clear all selections."""
        if self.multi_select:
            for checkbox in self.checkboxes.values():
                checkbox.setChecked(False)
        else:
            self.species_combo.setCurrentIndex(0)

    def filter_species(self, text):
        """Filter the species list based on the provided text.

        Args:
            text: Filter text
        """
        if not self.multi_select:
            return

        filter_text = text.lower()
        for species, checkbox in self.checkboxes.items():
            checkbox.setVisible(filter_text in species.lower())

    def on_selection_changed(self):
        """Handle changes in species selection."""
        selected = self.get_selected_species()
        self.selectionChanged.emit(selected)

    def on_combo_changed(self, index):
        """Handle changes in combo box selection."""
        if not self.multi_select:
            self.on_selection_changed()

    def set_selected_species(self, species_list):
        """Set the selected species from a list.

        Args:
            species_list: List of species names to select
        """
        if self.multi_select:
            for species, checkbox in self.checkboxes.items():
                checkbox.setChecked(species in species_list)
        else:
            # Find the index of the species in the combo box
            for i in range(1, self.species_combo.count()):
                if self.species_combo.itemText(i) in species_list:
                    self.species_combo.setCurrentIndex(i)
                    break
